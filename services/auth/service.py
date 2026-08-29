import uuid, hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_
from packages.common.exceptions import ConflictException, UnauthorizedException, NotFoundException, ValidationException
from packages.common.logger import get_logger
from packages.common.config import settings
from packages.security.crypto import hash_password, verify_password, generate_otp, generate_secure_token
from packages.security.jwt import create_access_token, create_refresh_token, decode_token
from packages.contracts.auth import RegisterRequest, LoginRequest, OTPRequest, OTPVerifyRequest, TokenResponse, SessionInfo
from packages.events.bus import get_event_bus
from packages.events.schemas import UserOnlineEvent
from .models import User, Device, UserSession, OTPRecord, LoginHistory

logger = get_logger("auth-service")

def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, req: RegisterRequest, ip_address: Optional[str] = None) -> Tuple[User, TokenResponse]:
        stmt = select(User).where(User.username == req.username)
        res = await self.db.execute(stmt)
        if res.scalar_one_or_none():
            raise ConflictException(f"Username '{req.username}' is already registered")

        if req.email:
            stmt = select(User).where(User.email == req.email)
            res = await self.db.execute(stmt)
            if res.scalar_one_or_none():
                raise ConflictException(f"Email '{req.email}' is already registered")

        if req.phone_number:
            stmt = select(User).where(User.phone_number == req.phone_number)
            res = await self.db.execute(stmt)
            if res.scalar_one_or_none():
                raise ConflictException(f"Phone number '{req.phone_number}' is already registered")

        user = User(
            username=req.username,
            display_name=req.display_name,
            email=req.email,
            phone_number=req.phone_number,
            hashed_password=hash_password(req.password),
            is_active=True,
            is_verified=False
        )
        self.db.add(user)
        await self.db.flush()

        device_id = str(uuid.uuid4())
        device = Device(
            user_id=user.id,
            device_id=device_id,
            device_name=req.device_name or "Primary Device",
            device_type=req.device_type or "web",
            last_ip=ip_address,
            last_active=datetime.now(timezone.utc),
            is_active=True
        )
        self.db.add(device)
        await self.db.flush()

        access_token = create_access_token(user_id=user.id, device_id=device_id, username=user.username, role=user.role)
        refresh_token = create_refresh_token(user_id=user.id, device_id=device_id)

        rf_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        session = UserSession(
            user_id=user.id,
            device_id=device.id,
            refresh_token_hash=rf_hash,
            ip_address=ip_address,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        self.db.add(session)
        self.db.add(LoginHistory(user_id=user.id, device_id=device_id, ip_address=ip_address, status="SUCCESS"))
        await self.db.commit()

        token_resp = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user.id,
            device_id=device_id
        )
        return user, token_resp

    async def login(self, req: LoginRequest, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Tuple[User, TokenResponse]:
        stmt = select(User).where(
            or_(User.username == req.identifier, User.email == req.identifier, User.phone_number == req.identifier)
        )
        res = await self.db.execute(stmt)
        user = res.scalar_one_or_none()

        if not user or not verify_password(req.password, user.hashed_password):
            if user:
                self.db.add(LoginHistory(user_id=user.id, device_id=req.device_id, ip_address=ip_address, user_agent=user_agent, status="FAILED"))
                await self.db.commit()
            raise UnauthorizedException("Invalid credentials")

        if not user.is_active:
            raise UnauthorizedException("Account is disabled")

        device_id = req.device_id or str(uuid.uuid4())
        stmt = select(Device).where(and_(Device.user_id == user.id, Device.device_id == device_id))
        res = await self.db.execute(stmt)
        device = res.scalar_one_or_none()

        if not device:
            device = Device(
                user_id=user.id,
                device_id=device_id,
                device_name=req.device_name or "Unknown Device",
                device_type=req.device_type or "web",
                last_ip=ip_address,
                last_active=datetime.now(timezone.utc),
                is_active=True
            )
            self.db.add(device)
            await self.db.flush()
        else:
            device.last_ip = ip_address
            device.last_active = datetime.now(timezone.utc)
            device.is_active = True

        access_token = create_access_token(user_id=user.id, device_id=device_id, username=user.username, role=user.role)
        refresh_token = create_refresh_token(user_id=user.id, device_id=device_id)

        rf_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        session = UserSession(
            user_id=user.id,
            device_id=device.id,
            refresh_token_hash=rf_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        self.db.add(session)
        self.db.add(LoginHistory(user_id=user.id, device_id=device_id, ip_address=ip_address, user_agent=user_agent, status="SUCCESS"))
        await self.db.commit()

        bus = get_event_bus()
        await bus.publish("presence.events", UserOnlineEvent(partition_key=user.id, user_id=user.id, device_id=device_id))

        token_resp = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user.id,
            device_id=device_id
        )
        return user, token_resp

    async def refresh_tokens(self, refresh_token: str, device_id: str, ip_address: Optional[str] = None) -> TokenResponse:
        claims = decode_token(refresh_token)
        if claims.token_type != "refresh":
            raise UnauthorizedException("Invalid token type for refresh")

        rf_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        stmt = select(UserSession).where(
            and_(UserSession.user_id == claims.sub, UserSession.refresh_token_hash == rf_hash, UserSession.is_revoked == False)
        )
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()

        if not session:
            raise UnauthorizedException("Session revoked or expired")

        stmt = select(User).where(User.id == claims.sub)
        res = await self.db.execute(stmt)
        user = res.scalar_one_or_none()
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        session.is_revoked = True
        new_access_token = create_access_token(user_id=user.id, device_id=device_id, username=user.username, role=user.role)
        new_refresh_token = create_refresh_token(user_id=user.id, device_id=device_id)

        new_rf_hash = hashlib.sha256(new_refresh_token.encode()).hexdigest()
        new_session = UserSession(
            user_id=user.id,
            device_id=session.device_id,
            refresh_token_hash=new_rf_hash,
            ip_address=ip_address,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        self.db.add(new_session)
        await self.db.commit()

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user.id,
            device_id=device_id
        )

    async def generate_otp(self, req: OTPRequest) -> str:
        code = generate_otp(6)
        expires = datetime.now(timezone.utc) + timedelta(seconds=settings.OTP_EXPIRE_SECONDS)
        record = OTPRecord(target=req.target, channel=req.channel, code=code, expires_at=expires)
        self.db.add(record)
        await self.db.commit()
        logger.info(f"Generated OTP [{code}] for target [{req.target}] via channel [{req.channel}]")
        return code

    async def verify_otp(self, req: OTPVerifyRequest) -> bool:
        stmt = select(OTPRecord).where(
            and_(OTPRecord.target == req.target, OTPRecord.is_consumed == False)
        ).order_by(OTPRecord.created_at.desc())
        res = await self.db.execute(stmt)
        record = res.scalars().first()

        if not record:
            raise ValidationException("No active OTP found for this target")

        if _ensure_utc(record.expires_at) < datetime.now(timezone.utc):
            raise ValidationException("OTP has expired")

        if record.code != req.code:
            record.attempts += 1
            await self.db.commit()
            raise ValidationException("Invalid OTP code")

        record.is_consumed = True
        await self.db.commit()
        return True

    async def list_sessions(self, user_id: str) -> List[SessionInfo]:
        stmt = select(UserSession, Device).join(Device, UserSession.device_id == Device.id).where(
            and_(UserSession.user_id == user_id, UserSession.is_revoked == False)
        )
        res = await self.db.execute(stmt)
        sessions = []
        for sess, dev in res.all():
            sessions.append(SessionInfo(
                id=sess.id,
                user_id=sess.user_id,
                device_id=dev.device_id,
                device_name=dev.device_name,
                device_type=dev.device_type,
                ip_address=sess.ip_address,
                last_active=_ensure_utc(dev.last_active),
                is_current=False
            ))
        return sessions

    async def revoke_session(self, user_id: str, session_id: str) -> bool:
        stmt = update(UserSession).where(
            and_(UserSession.user_id == user_id, UserSession.id == session_id)
        ).values(is_revoked=True)
        await self.db.execute(stmt)
        await self.db.commit()
        return True
