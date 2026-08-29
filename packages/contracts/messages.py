from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
from pydantic import Field
from .models import TimestampedModel, BaseDTO

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    VOICE_NOTE = "voice_note"
    DOCUMENT = "document"
    LOCATION = "location"
    STICKER = "sticker"
    GIF = "gif"
    SYSTEM = "system"

class DeliveryState(str, Enum):
    SENDING = "sending"
    SENT = "sent"
    SERVER_ACCEPTED = "server_accepted"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class SendMessageRequest(BaseDTO):
    idempotency_key: str = Field(..., description="Unique idempotency key")
    conversation_id: str
    message_type: MessageType = MessageType.TEXT
    content: str
    media_url: Optional[str] = None
    media_metadata: Optional[Dict[str, Any]] = None
    reply_to_message_id: Optional[str] = None
    mentions: List[str] = []

class EditMessageRequest(BaseDTO):
    content: str

class MessageReactionRequest(BaseDTO):
    emoji: str

class MessageDTO(TimestampedModel):
    conversation_id: str
    sender_id: str
    sender_device_id: Optional[str] = None
    sequence_number: int = 0
    lamport_clock: int = 0
    idempotency_key: str = ""
    message_type: str = "text"
    content: str = ""
    media_url: Optional[str] = None
    media_metadata: Optional[Dict[str, Any]] = None
    reply_to_message_id: Optional[str] = None
    mentions: List[str] = []
    delivery_state: str = "sent"
    is_edited: bool = False
    edited_at: Optional[datetime] = None
    is_deleted_for_everyone: bool = False
    is_pinned: bool = False
    reactions: Dict[str, List[str]] = {}
