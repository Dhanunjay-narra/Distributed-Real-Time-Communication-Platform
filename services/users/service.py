from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, or_, and_
from packages.common.exceptions import NotFoundException, ConflictException
from services.auth.models import User
from services.users.models import UserPreference
from packages.contracts.users import UserProfileDTO, UpdateProfileRequest, UserPreferencesDTO

def _ensure_utc(dt: datetime) -> datetime:
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt or datetime.now(timezone.utc)

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_profile(self, user_id: str) -> UserProfileDTO:
        stmt = select(User).where(User.id == user_id)
        res = await self.db.execute(stmt)
        user = res.scalar_one_or_none()
        if not user:
            raise NotFoundException(f"User {user_id} not found")
        return UserProfileDTO(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            email=user.email,
            phone_number=user.phone_number,
            avatar_url=user.avatar_url,
            about=user.about,
            bio=user.bio,
            is_verified=user.is_verified,
            presence_status="ONLINE" if user.is_active else "OFFLINE",
            created_at=_ensure_utc(user.created_at),
            updated_at=_ensure_utc(user.updated_at)
        )

    async def update_profile(self, user_id: str, req: UpdateProfileRequest) -> UserProfileDTO:
        stmt = select(User).where(User.id == user_id)
        res = await self.db.execute(stmt)
        user = res.scalar_one_or_none()
        if not user:
            raise NotFoundException(f"User {user_id} not found")

        if req.display_name is not None: user.display_name = req.display_name
        if req.avatar_url is not None: user.avatar_url = req.avatar_url
        if req.about is not None: user.about = req.about
        if req.bio is not None: user.bio = req.bio
        user.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(user)
        return await self.get_profile(user_id)

    async def search_users(self, query: str, limit: int = 20) -> List[UserProfileDTO]:
        q = f"%{query}%"
        stmt = select(User).where(
            or_(User.username.ilike(q), User.display_name.ilike(q), User.email.ilike(q), User.phone_number.ilike(q))
        ).limit(limit)
        res = await self.db.execute(stmt)
        users = res.scalars().all()
        return [
            UserProfileDTO(
                id=u.id,
                username=u.username,
                display_name=u.display_name,
                email=u.email,
                phone_number=u.phone_number,
                avatar_url=u.avatar_url,
                about=u.about,
                bio=u.bio,
                is_verified=u.is_verified,
                created_at=_ensure_utc(u.created_at),
                updated_at=_ensure_utc(u.updated_at)
            ) for u in users
        ]
