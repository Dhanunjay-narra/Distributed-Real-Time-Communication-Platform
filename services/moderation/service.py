from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, desc
from packages.common.exceptions import NotFoundException
from packages.contracts.moderation import CreateReportRequest, ReportReason, ApplySanctionRequest, SanctionType
from .models import ContentReport, UserSanction

def _ensure_utc(dt: datetime) -> datetime:
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt or datetime.now(timezone.utc)

class ModerationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.spam_keywords = {"buy_crypto_fast", "free_gift_cards", "phishing_link"}

    def scan_content(self, text: str) -> bool:
        text_lower = text.lower()
        return any(kw in text_lower for kw in self.spam_keywords)

    async def submit_report(self, reporter_id: str, req: CreateReportRequest) -> ContentReport:
        report = ContentReport(
            reporter_id=reporter_id,
            reported_user_id=req.reported_user_id,
            message_id=req.message_id,
            conversation_id=req.conversation_id,
            reason=req.reason.value if hasattr(req.reason, "value") else str(req.reason),
            description=req.description,
            status="PENDING"
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def apply_sanction(self, req: ApplySanctionRequest) -> UserSanction:
        expires = None
        if req.duration_hours:
            expires = datetime.now(timezone.utc) + timedelta(hours=req.duration_hours)

        sanction = UserSanction(
            user_id=req.user_id,
            sanction_type=req.sanction_type.value if hasattr(req.sanction_type, "value") else str(req.sanction_type),
            reason=req.reason,
            expires_at=expires,
            is_active=True
        )
        self.db.add(sanction)
        await self.db.commit()
        await self.db.refresh(sanction)
        return sanction

    async def is_user_banned(self, user_id: str) -> bool:
        stmt = select(UserSanction).where(
            and_(UserSanction.user_id == user_id, UserSanction.is_active == True)
        )
        res = await self.db.execute(stmt)
        sanctions = res.scalars().all()
        now = datetime.now(timezone.utc)

        for s in sanctions:
            if s.sanction_type in ["permanent_ban", "temporary_ban"]:
                if s.expires_at is None or _ensure_utc(s.expires_at) > now:
                    return True
        return False
