from typing import Optional
from datetime import datetime
from enum import Enum
from .models import BaseDTO

class PresenceStatus(str, Enum):
    ONLINE = "ONLINE"
    AWAY = "AWAY"
    IDLE = "IDLE"
    OFFLINE = "OFFLINE"
    DND = "DND"

class PresenceHeartbeat(BaseDTO):
    user_id: str
    device_id: str
    status: PresenceStatus = PresenceStatus.ONLINE
    custom_status: Optional[str] = None

class TypingIndicatorDTO(BaseDTO):
    conversation_id: str
    user_id: str
    is_typing: bool
    timestamp: datetime
