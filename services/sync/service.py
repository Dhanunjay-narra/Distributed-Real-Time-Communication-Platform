from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from packages.contracts.sync import SyncPullRequest, SyncDeltaResponse
from packages.contracts.messages import MessageDTO, SendMessageRequest
from services.conversations.models import Conversation, ConversationParticipant, Message
from services.messaging.service import MessagingService
from .vector_clock import VectorClock

def _ensure_utc(dt: datetime) -> datetime:
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt or datetime.now(timezone.utc)

class SyncService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.msg_svc = MessagingService(db)

    async def pull_deltas(self, user_id: str, req: SyncPullRequest) -> SyncDeltaResponse:
        stmt = select(ConversationParticipant.conversation_id, ConversationParticipant.last_read_sequence).where(
            ConversationParticipant.user_id == user_id
        )
        res = await self.db.execute(stmt)
        conv_rows = res.all()
        conv_ids = [row[0] for row in conv_rows]
        read_states = {row[0]: row[1] for row in conv_rows}

        if not conv_ids:
            return SyncDeltaResponse(latest_sequence=req.since_sequence, messages=[], read_states={}, has_more=False)

        stmt_msgs = select(Message).where(
            and_(Message.conversation_id.in_(conv_ids), Message.sequence_number > req.since_sequence)
        ).order_by(Message.sequence_number.asc()).limit(req.limit)
        
        res_msgs = await self.db.execute(stmt_msgs)
        messages = res_msgs.scalars().all()

        message_dtos = [await self.msg_svc._to_dto(m) for m in messages]
        max_seq = max([m.sequence_number for m in messages], default=req.since_sequence)
        has_more = len(messages) == req.limit

        return SyncDeltaResponse(
            latest_sequence=max_seq,
            messages=message_dtos,
            read_states=read_states,
            deleted_message_ids=[m.id for m in messages if m.is_deleted_for_everyone],
            has_more=has_more
        )

    async def reconcile_offline_outbox(self, user_id: str, device_id: str, outbox_messages: List[SendMessageRequest]) -> List[MessageDTO]:
        synced_messages = []
        for req in outbox_messages:
            dto = await self.msg_svc.send_message(sender_id=user_id, req=req, sender_device_id=device_id)
            synced_messages.append(dto)
        return synced_messages
