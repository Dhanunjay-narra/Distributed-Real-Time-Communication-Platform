from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_, or_
from packages.common.exceptions import ConflictException, NotFoundException, ValidationException
from services.users.models import BlockedUser, PrivacySettings
from services.users.service import UserService

def _ensure_utc(dt: datetime) -> datetime:
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt or datetime.now(timezone.utc)

class PrivacyService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_svc = UserService(db)

    async def block_user(self, user_id: str, target_user_id: str, reason: Optional[str] = None) -> bool:
        if user_id == target_user_id:
            raise ValidationException("Cannot block yourself")

        stmt = select(BlockedUser).where(and_(BlockedUser.user_id == user_id, BlockedUser.blocked_user_id == target_user_id))
        res = await self.db.execute(stmt)
        if res.scalar_one_or_none():
            return True

        record = BlockedUser(user_id=user_id, blocked_user_id=target_user_id, reason=reason)
        self.db.add(record)
        await self.db.commit()
        return True

    async def unblock_user(self, user_id: str, target_user_id: str) -> bool:
        stmt = delete(BlockedUser).where(and_(BlockedUser.user_id == user_id, BlockedUser.blocked_user_id == target_user_id))
        await self.db.execute(stmt)
        await self.db.commit()
        return True

    async def is_blocked(self, user_a: str, user_b: str) -> bool:
        stmt = select(BlockedUser).where(
            or_(
                and_(BlockedUser.user_id == user_a, BlockedUser.blocked_user_id == user_b),
                and_(BlockedUser.user_id == user_b, BlockedUser.blocked_user_id == user_a)
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none() is not None

    async def list_blocked_users(self, user_id: str) -> List[str]:
        stmt = select(BlockedUser.blocked_user_id).where(BlockedUser.user_id == user_id)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_privacy_settings(self, user_id: str) -> PrivacySettings:
        stmt = select(PrivacySettings).where(PrivacySettings.user_id == user_id)
        res = await self.db.execute(stmt)
        settings = res.scalar_one_or_none()
        if not settings:
            settings = PrivacySettings(user_id=user_id)
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)
        return settings

    async def update_privacy_settings(self, user_id: str, last_seen: Optional[str] = None, read_receipts: Optional[bool] = None, typing_indicators: Optional[bool] = None) -> PrivacySettings:
        settings = await self.get_privacy_settings(user_id)
        if last_seen is not None: settings.last_seen_visibility = last_seen
        if read_receipts is not None: settings.read_receipts_enabled = read_receipts
        if typing_indicators is not None: settings.typing_indicator_enabled = typing_indicators
        settings.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(settings)
        return settings
