import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class DomainEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None
    partition_key: str

    def to_payload(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")

class MessageSentEvent(DomainEvent):
    event_type: str = "message.sent"
    message_id: str
    conversation_id: str
    sender_id: str
    sender_device_id: Optional[str] = None
    sequence_number: int
    content: str
    message_type: str = "text"
    media_url: Optional[str] = None
    reply_to_message_id: Optional[str] = None
    participant_ids: List[str] = []

class MessageDeliveredEvent(DomainEvent):
    event_type: str = "message.delivered"
    message_id: str
    conversation_id: str
    recipient_id: str
    device_id: str

class MessageReadEvent(DomainEvent):
    event_type: str = "message.read"
    message_id: str
    conversation_id: str
    reader_id: str
    read_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MessageEditedEvent(DomainEvent):
    event_type: str = "message.edited"
    message_id: str
    conversation_id: str
    new_content: str
    edited_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MessageDeletedEvent(DomainEvent):
    event_type: str = "message.deleted"
    message_id: str
    conversation_id: str
    deleted_for_everyone: bool = True

class UserOnlineEvent(DomainEvent):
    event_type: str = "user.online"
    user_id: str
    device_id: str

class UserOfflineEvent(DomainEvent):
    event_type: str = "user.offline"
    user_id: str
    device_id: str
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GroupCreatedEvent(DomainEvent):
    event_type: str = "group.created"
    group_id: str
    conversation_id: str
    name: str
    creator_id: str
    member_ids: List[str] = []

class MemberAddedEvent(DomainEvent):
    event_type: str = "group.member_added"
    group_id: str
    conversation_id: str
    user_id: str
    added_by: str
    role: str = "member"

class MediaUploadedEvent(DomainEvent):
    event_type: str = "media.uploaded"
    media_id: str
    user_id: str
    storage_key: str
    content_type: str
    file_size_bytes: int

class CallSignalingEvent(DomainEvent):
    event_type: str = "call.signaling"
    call_id: str
    sender_id: str
    recipient_id: Optional[str] = None
    signal_type: str
    payload: Dict[str, Any] = {}

class NotificationRequestedEvent(DomainEvent):
    event_type: str = "notification.requested"
    recipient_id: str
    title: str
    body: str
    data: Dict[str, Any] = {}
    channel: str = "push"

class SagaStepEvent(DomainEvent):
    event_type: str = "saga.step"
    saga_id: str
    saga_name: str
    step: str
    status: str
    payload: Dict[str, Any] = {}
