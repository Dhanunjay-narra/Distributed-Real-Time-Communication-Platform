from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from services.conversations.models import Message, Conversation, ConversationParticipant
from services.messaging.service import MessagingService
from packages.contracts.messages import MessageDTO

class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.msg_svc = MessagingService(db)

    async def search_messages(
        self,
        user_id: str,
        query: str,
        conversation_id: Optional[str] = None,
        sender_id: Optional[str] = None,
        limit: int = 20
    ) -> List[MessageDTO]:
        # Ensure user can only search in conversations they participate in
        stmt_convs = select(ConversationParticipant.conversation_id).where(
            ConversationParticipant.user_id == user_id
        )
        res_convs = await self.db.execute(stmt_convs)
        allowed_conv_ids = res_convs.scalars().all()

        if not allowed_conv_ids:
            return []

        q = f"%{query}%"
        stmt = select(Message).where(
            and_(
                Message.conversation_id.in_(allowed_conv_ids),
                Message.content.ilike(q),
                Message.is_deleted_for_everyone == False
            )
        )
        if conversation_id and conversation_id in allowed_conv_ids:
            stmt = stmt.where(Message.conversation_id == conversation_id)
        if sender_id:
            stmt = stmt.where(Message.sender_id == sender_id)

        stmt = stmt.order_by(desc(Message.created_at)).limit(limit)
        res = await self.db.execute(stmt)
        messages = res.scalars().all()

        return [await self.msg_svc._to_dto(m) for m in messages]
