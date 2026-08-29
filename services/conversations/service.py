from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, desc
from packages.common.exceptions import NotFoundException, ForbiddenException, ConflictException
from packages.contracts.conversations import CreateConversationRequest, ConversationDTO, ConversationType
from services.auth.models import User
from services.conversations.models import Conversation, ConversationParticipant, Message
from services.users.service import UserService

def _ensure_utc(dt: datetime) -> datetime:
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt or datetime.now(timezone.utc)

class ConversationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_svc = UserService(db)

    async def create_or_get_direct(self, user_id: str, recipient_id: str) -> ConversationDTO:
        # Check if direct conversation already exists between the two participants
        stmt = select(Conversation).join(ConversationParticipant).where(
            and_(Conversation.type == "direct", ConversationParticipant.user_id.in_([user_id, recipient_id]))
        )
        res = await self.db.execute(stmt)
        conversations = res.scalars().unique().all()

        for conv in conversations:
            p_stmt = select(ConversationParticipant.user_id).where(ConversationParticipant.conversation_id == conv.id)
            p_res = await self.db.execute(p_stmt)
            p_ids = set(p_res.scalars().all())
            if p_ids == {user_id, recipient_id}:
                return await self.get_conversation(conv.id, user_id)

        # Create new direct conversation
        conv = Conversation(type="direct", created_by=user_id, sequence_counter=0)
        self.db.add(conv)
        await self.db.flush()

        p1 = ConversationParticipant(conversation_id=conv.id, user_id=user_id, role="member")
        p2 = ConversationParticipant(conversation_id=conv.id, user_id=recipient_id, role="member")
        self.db.add_all([p1, p2])
        await self.db.commit()
        await self.db.refresh(conv)

        return await self.get_conversation(conv.id, user_id)

    async def get_conversation(self, conversation_id: str, user_id: str) -> ConversationDTO:
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        res = await self.db.execute(stmt)
        conv = res.scalar_one_or_none()
        if not conv:
            raise NotFoundException("Conversation not found")

        # Get participant status for user
        stmt_p = select(ConversationParticipant).where(
            and_(ConversationParticipant.conversation_id == conversation_id, ConversationParticipant.user_id == user_id)
        )
        res_p = await self.db.execute(stmt_p)
        my_p = res_p.scalar_one_or_none()
        if not my_p:
            raise ForbiddenException("You are not a participant in this conversation")

        # Load all participants
        stmt_all = select(ConversationParticipant.user_id).where(ConversationParticipant.conversation_id == conversation_id)
        res_all = await self.db.execute(stmt_all)
        p_ids = res_all.scalars().all()

        profiles = []
        for pid in p_ids:
            try:
                profiles.append(await self.user_svc.get_profile(pid))
            except Exception: pass

        return ConversationDTO(
            id=conv.id,
            type=conv.type,
            title=conv.title,
            avatar_url=conv.avatar_url,
            created_by=conv.created_by,
            last_message_id=conv.last_message_id,
            last_message_preview=conv.last_message_preview,
            last_message_timestamp=_ensure_utc(conv.last_message_timestamp) if conv.last_message_timestamp else None,
            unread_count=my_p.unread_count,
            is_pinned=my_p.is_pinned,
            is_muted=my_p.is_muted,
            participants=profiles,
            sync_cursor=conv.sequence_counter,
            created_at=_ensure_utc(conv.created_at),
            updated_at=_ensure_utc(conv.updated_at)
        )

    async def list_user_conversations(self, user_id: str) -> List[ConversationDTO]:
        stmt = select(ConversationParticipant.conversation_id).where(ConversationParticipant.user_id == user_id)
        res = await self.db.execute(stmt)
        conv_ids = res.scalars().all()

        results = []
        for cid in conv_ids:
            try:
                results.append(await self.get_conversation(cid, user_id))
            except Exception: pass
        results.sort(key=lambda c: (c.is_pinned, c.last_message_timestamp or c.created_at), reverse=True)
        return results

    async def toggle_pin(self, conversation_id: str, user_id: str) -> bool:
        stmt = select(ConversationParticipant).where(
            and_(ConversationParticipant.conversation_id == conversation_id, ConversationParticipant.user_id == user_id)
        )
        res = await self.db.execute(stmt)
        p = res.scalar_one_or_none()
        if not p: raise NotFoundException("Conversation not found")
        p.is_pinned = not p.is_pinned
        await self.db.commit()
        return p.is_pinned

    async def toggle_mute(self, conversation_id: str, user_id: str) -> bool:
        stmt = select(ConversationParticipant).where(
            and_(ConversationParticipant.conversation_id == conversation_id, ConversationParticipant.user_id == user_id)
        )
        res = await self.db.execute(stmt)
        p = res.scalar_one_or_none()
        if not p: raise NotFoundException("Conversation not found")
        p.is_muted = not p.is_muted
        await self.db.commit()
        return p.is_muted
