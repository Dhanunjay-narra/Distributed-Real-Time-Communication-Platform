import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import relationship
from packages.common.database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String(20), default="direct", nullable=False)  # 'direct', 'group', 'channel'
    title = Column(String(200), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    last_message_id = Column(String(36), nullable=True)
    last_message_preview = Column(String(500), nullable=True)
    last_message_timestamp = Column(DateTime(timezone=True), nullable=True)
    sequence_counter = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    participants = relationship("ConversationParticipant", back_populates="conversation", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class ConversationParticipant(Base):
    __tablename__ = "conversation_participants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), default="member")  # 'owner', 'admin', 'moderator', 'member'
    last_read_message_id = Column(String(36), nullable=True)
    last_read_sequence = Column(Integer, default=0)
    unread_count = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False)
    is_muted = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    conversation = relationship("Conversation", back_populates="participants")

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    sender_device_id = Column(String(100), nullable=True)
    idempotency_key = Column(String(100), index=True, nullable=False)
    sequence_number = Column(Integer, nullable=False, index=True)
    lamport_clock = Column(Integer, default=0, nullable=False)
    message_type = Column(String(30), default="text", nullable=False)
    content = Column(Text, nullable=False)
    media_url = Column(String(500), nullable=True)
    media_metadata = Column(JSON, nullable=True)
    reply_to_message_id = Column(String(36), ForeignKey("messages.id"), nullable=True)
    forwarded_from_message_id = Column(String(36), nullable=True)
    mentions = Column(JSON, default=list)
    delivery_state = Column(String(30), default="sent")
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted_for_everyone = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    conversation = relationship("Conversation", back_populates="messages")
    reactions = relationship("MessageReaction", back_populates="message", cascade="all, delete-orphan")

class MessageReaction(Base):
    __tablename__ = "message_reactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    emoji = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    message = relationship("Message", back_populates="reactions")
