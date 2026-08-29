from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from services.auth.models import User
from services.conversations.models import Conversation, Message
from services.moderation.models import ContentReport
from services.analytics.service import analytics_engine

class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_system_telemetry(self) -> dict:
        total_users = await self.db.scalar(select(func.count(User.id)))
        total_convs = await self.db.scalar(select(func.count(Conversation.id)))
        total_msgs = await self.db.scalar(select(func.count(Message.id)))
        pending_reports = await self.db.scalar(select(func.count(ContentReport.id)).where(ContentReport.status == "PENDING"))

        telemetry = analytics_engine.get_dashboard_metrics()
        telemetry.update({
            "total_registered_users": total_users or 0,
            "total_conversations": total_convs or 0,
            "persisted_messages": total_msgs or 0,
            "pending_reports_queue": pending_reports or 0,
            "cluster_status": "ONLINE"
        })
        return telemetry
