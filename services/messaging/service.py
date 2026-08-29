from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, desc
from packages.common.exceptions import NotFoundException, ForbiddenException, ConflictException, ValidationException
from packages.common.redis_client import get_redis_client
from packages.contracts.messages import SendMessageRequest, EditMessageRequest, MessageDTO, DeliveryState
from packages.events.bus import get_event_bus
from packages.events.schemas import MessageSentEvent, MessageDeliveredEvent, MessageReadEvent
from services.conversations.models import Conversation, ConversationParticipant, Message, MessageReaction
from services.privacy.service import PrivacyService

def _ensure_utc(dt: datetime) -> datetime:
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt or datetime.now(timezone.utc)

class MessagingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.privacy_svc = PrivacyService(db)

    async def send_message(self, sender_id: str, req: SendMessageRequest, sender_device_id: Optional[str] = None) -> MessageDTO:
        # 1. Distributed Idempotency Filter (Redis Cache + DB Fallback)
        redis = await get_redis_client()
        idemp_key = f"idempotency:{req.idempotency_key}"
        cached_msg_id = await redis.get(idemp_key)
        if cached_msg_id:
            return await self.get_message(cached_msg_id)

        # Persistent DB idempotency check
        stmt_idemp = select(Message).where(
            and_(Message.conversation_id == req.conversation_id, Message.idempotency_key == req.idempotency_key)
        )
        res_idemp = await self.db.execute(stmt_idemp)
        existing_msg = res_idemp.scalar_one_or_none()
        if existing_msg:
            await redis.set(idemp_key, existing_msg.id, expire_seconds=86400)
            return await self._to_dto(existing_msg)

        # 2. Check conversation membership
        stmt = select(ConversationParticipant).where(
            and_(ConversationParticipant.conversation_id == req.conversation_id, ConversationParticipant.user_id == sender_id)
        )
        res = await self.db.execute(stmt)
        p = res.scalar_one_or_none()
        if not p:
            raise ForbiddenException("You are not a participant in this conversation")

        # 3. Check privacy blocks if direct chat
        stmt_conv = select(Conversation).where(Conversation.id == req.conversation_id)
        res_conv = await self.db.execute(stmt_conv)
        conv = res_conv.scalar_one_or_none()
        if not conv:
            raise NotFoundException("Conversation not found")

        if conv.type == "direct":
            stmt_other = select(ConversationParticipant.user_id).where(
                and_(ConversationParticipant.conversation_id == req.conversation_id, ConversationParticipant.user_id != sender_id)
            )
            res_other = await self.db.execute(stmt_other)
            other_user_id = res_other.scalar_one_or_none()
            if other_user_id and await self.privacy_svc.is_blocked(sender_id, other_user_id):
                raise ForbiddenException("Cannot send message. Communication is blocked.")

        # 4. Partition-Aware Monotonic Sequence Allocation
        conv.sequence_counter += 1
        sequence_num = conv.sequence_counter
        lamport_clock = sequence_num * 10 + 1

        message = Message(
            conversation_id=req.conversation_id,
            sender_id=sender_id,
            sender_device_id=sender_device_id,
            idempotency_key=req.idempotency_key,
            sequence_number=sequence_num,
            lamport_clock=lamport_clock,
            message_type=req.message_type,
            content=req.content,
            media_url=req.media_url,
            media_metadata=req.media_metadata,
            reply_to_message_id=req.reply_to_message_id,
            mentions=req.mentions,
            delivery_state=DeliveryState.SERVER_ACCEPTED,
        )
        self.db.add(message)
        await self.db.flush()

        conv.last_message_id = message.id
        conv.last_message_preview = (req.content[:80] + "...") if len(req.content) > 80 else req.content
        conv.last_message_timestamp = datetime.now(timezone.utc)

        stmt_upd = update(ConversationParticipant).where(
            and_(ConversationParticipant.conversation_id == req.conversation_id, ConversationParticipant.user_id != sender_id)
        ).values(unread_count=ConversationParticipant.unread_count + 1)
        await self.db.execute(stmt_upd)

        await self.db.commit()
        await self.db.refresh(message)

        await redis.set(idemp_key, message.id, expire_seconds=86400)

        # 5. Publish Domain Event to Event Backbone
        bus = get_event_bus()
        evt = MessageSentEvent(
            partition_key=req.conversation_id,
            message_id=message.id,
            conversation_id=req.conversation_id,
            sender_id=sender_id,
            sender_device_id=sender_device_id,
            sequence_number=sequence_num,
            content=req.content,
            message_type=req.message_type,
            media_url=req.media_url,
            reply_to_message_id=req.reply_to_message_id
        )
        await bus.publish("messages.sent", evt)

        return await self._to_dto(message)

    async def get_message(self, message_id: str) -> MessageDTO:
        stmt = select(Message).where(Message.id == message_id)
        res = await self.db.execute(stmt)
        message = res.scalar_one_or_none()
        if not message:
            raise NotFoundException("Message not found")
        return await self._to_dto(message)

    async def list_messages(self, conversation_id: str, limit: int = 50, before_sequence: Optional[int] = None) -> List[MessageDTO]:
        stmt = select(Message).where(Message.conversation_id == conversation_id)
        if before_sequence:
            stmt = stmt.where(Message.sequence_number < before_sequence)
        stmt = stmt.order_by(desc(Message.sequence_number)).limit(limit)
        res = await self.db.execute(stmt)
        messages = res.scalars().all()
        return [await self._to_dto(m) for m in reversed(messages)]

    async def edit_message(self, message_id: str, user_id: str, req: EditMessageRequest) -> MessageDTO:
        stmt = select(Message).where(Message.id == message_id)
        res = await self.db.execute(stmt)
        message = res.scalar_one_or_none()
        if not message: raise NotFoundException("Message not found")
        if message.sender_id != user_id: raise ForbiddenException("Cannot edit messages from other users")

        message.content = req.content
        message.is_edited = True
        message.edited_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(message)
        return await self._to_dto(message)

    async def delete_for_everyone(self, message_id: str, user_id: str) -> bool:
        stmt = select(Message).where(Message.id == message_id)
        res = await self.db.execute(stmt)
        message = res.scalar_one_or_none()
        if not message: raise NotFoundException("Message not found")
        if message.sender_id != user_id: raise ForbiddenException("Cannot delete messages from other users")

        message.is_deleted_for_everyone = True
        message.content = "This message was deleted"
        await self.db.commit()
        return True

    async def toggle_reaction(self, message_id: str, user_id: str, emoji: str) -> Dict[str, List[str]]:
        stmt = select(MessageReaction).where(
            and_(MessageReaction.message_id == message_id, MessageReaction.user_id == user_id, MessageReaction.emoji == emoji)
        )
        res = await self.db.execute(stmt)
        existing = res.scalar_one_or_none()

        if existing:
            await self.db.delete(existing)
        else:
            reaction = MessageReaction(message_id=message_id, user_id=user_id, emoji=emoji)
            self.db.add(reaction)

        await self.db.commit()
        return await self._get_reactions(message_id)

    async def mark_as_read(self, conversation_id: str, user_id: str, message_id: str) -> bool:
        stmt = select(Message).where(Message.id == message_id)
        res = await self.db.execute(stmt)
        msg = res.scalar_one_or_none()
        if not msg: return False

        stmt_p = update(ConversationParticipant).where(
            and_(ConversationParticipant.conversation_id == conversation_id, ConversationParticipant.user_id == user_id)
        ).values(last_read_message_id=message_id, last_read_sequence=msg.sequence_number, unread_count=0)
        await self.db.execute(stmt_p)

        msg.delivery_state = DeliveryState.READ
        await self.db.commit()

        bus = get_event_bus()
        await bus.publish("messages.read", MessageReadEvent(
            partition_key=conversation_id,
            message_id=message_id,
            conversation_id=conversation_id,
            reader_id=user_id
        ))
        return True

    async def _get_reactions(self, message_id: str) -> Dict[str, List[str]]:
        stmt = select(MessageReaction).where(MessageReaction.message_id == message_id)
        res = await self.db.execute(stmt)
        reactions = res.scalars().all()
        rx_map: Dict[str, List[str]] = {}
        for r in reactions:
            if r.emoji not in rx_map: rx_map[r.emoji] = []
            rx_map[r.emoji].append(r.user_id)
        return rx_map

    async def _to_dto(self, m: Message) -> MessageDTO:
        reactions = await self._get_reactions(m.id)
        return MessageDTO(
            id=m.id,
            conversation_id=m.conversation_id,
            sender_id=m.sender_id,
            sender_device_id=m.sender_device_id,
            sequence_number=m.sequence_number,
            lamport_clock=m.lamport_clock,
            idempotency_key=m.idempotency_key,
            message_type=m.message_type,
            content=m.content,
            media_url=m.media_url,
            media_metadata=m.media_metadata,
            reply_to_message_id=m.reply_to_message_id,
            mentions=m.mentions or [],
            delivery_state=m.delivery_state,
            is_edited=m.is_edited,
            edited_at=_ensure_utc(m.edited_at) if m.edited_at else None,
            is_deleted_for_everyone=m.is_deleted_for_everyone,
            is_pinned=m.is_pinned,
            reactions=reactions,
            created_at=_ensure_utc(m.created_at),
            updated_at=_ensure_utc(m.updated_at)
        )
