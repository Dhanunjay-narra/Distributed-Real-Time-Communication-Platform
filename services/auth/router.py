from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from packages.common.database import get_db_session
from packages.contracts.models import APIResponse
from packages.contracts.auth import RegisterRequest, LoginRequest, OTPRequest, OTPVerifyRequest, RefreshTokenRequest
from packages.security.jwt import decode_token
from .service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/register", response_model=APIResponse)
async def register(req: RegisterRequest, request: Request, db: AsyncSession = Depends(get_db_session)):
    svc = AuthService(db)
    client_ip = request.client.host if request.client else None
    user, tokens = await svc.register(req, ip_address=client_ip)
    return APIResponse(message="Registration successful", data=tokens.model_dump())

@router.post("/login", response_model=APIResponse)
async def login(req: LoginRequest, request: Request, db: AsyncSession = Depends(get_db_session)):
    svc = AuthService(db)
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    user, tokens = await svc.login(req, ip_address=client_ip, user_agent=user_agent)
    return APIResponse(message="Login successful", data=tokens.model_dump())

@router.post("/refresh", response_model=APIResponse)
async def refresh_tokens(req: RefreshTokenRequest, request: Request, db: AsyncSession = Depends(get_db_session)):
    svc = AuthService(db)
    client_ip = request.client.host if request.client else None
    tokens = await svc.refresh_tokens(req.refresh_token, device_id=req.device_id, ip_address=client_ip)
    return APIResponse(message="Tokens refreshed", data=tokens.model_dump())

@router.post("/otp/send", response_model=APIResponse)
async def send_otp(req: OTPRequest, db: AsyncSession = Depends(get_db_session)):
    svc = AuthService(db)
    code = await svc.generate_otp(req)
    return APIResponse(message="OTP sent successfully", data={"target": req.target, "channel": req.channel})

@router.post("/otp/verify", response_model=APIResponse)
async def verify_otp(req: OTPVerifyRequest, db: AsyncSession = Depends(get_db_session)):
    svc = AuthService(db)
    success = await svc.verify_otp(req)
    return APIResponse(message="OTP verified successfully", data={"verified": success})

@router.get("/sessions", response_model=APIResponse)
async def get_sessions(authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    token = authorization.replace("Bearer ", "")
    claims = decode_token(token)
    svc = AuthService(db)
    sessions = await svc.list_sessions(claims.sub)
    return APIResponse(data=[s.model_dump() for s in sessions])

@router.delete("/sessions/{session_id}", response_model=APIResponse)
async def revoke_session(session_id: str, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    token = authorization.replace("Bearer ", "")
    claims = decode_token(token)
    svc = AuthService(db)
    await svc.revoke_session(claims.sub, session_id)
    return APIResponse(message="Session revoked")
