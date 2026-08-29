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
    sequence_number: int
    content: str
    message_type: str = "text"
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

class UserOnlineEvent(DomainEvent):
    event_type: str = "user.online"
    user_id: str
    device_id: str

class UserOfflineEvent(DomainEvent):
    event_type: str = "user.offline"
    user_id: str
    device_id: str
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
