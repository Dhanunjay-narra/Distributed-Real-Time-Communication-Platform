from typing import Optional, List
from datetime import datetime
from enum import Enum
from .models import TimestampedModel, BaseDTO
from .users import UserProfileDTO

class ConversationType(str, Enum):
    DIRECT = "direct"
    GROUP = "group"
    CHANNEL = "channel"

class CreateConversationRequest(BaseDTO):
    type: ConversationType = ConversationType.DIRECT
    recipient_id: Optional[str] = None
    title: Optional[str] = None
    participant_ids: List[str] = []

class ConversationDTO(TimestampedModel):
    type: ConversationType
    title: Optional[str] = None
    avatar_url: Optional[str] = None
    created_by: str
    last_message_id: Optional[str] = None
    last_message_preview: Optional[str] = None
    last_message_timestamp: Optional[datetime] = None
    unread_count: int = 0
    is_pinned: bool = False
    is_muted: bool = False
    participants: List[UserProfileDTO] = []
    sync_cursor: int = 0
