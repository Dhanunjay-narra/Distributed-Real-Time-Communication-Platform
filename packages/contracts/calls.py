from typing import Optional, Dict, Any
from enum import Enum
from .models import TimestampedModel, BaseDTO

class CallType(str, Enum):
    VOICE = "voice"
    VIDEO = "video"

class CallState(str, Enum):
    INITIATED = "initiated"
    RINGING = "ringing"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ENDED = "ended"
    MISSED = "missed"
    REJECTED = "rejected"
    BUSY = "busy"

class CallSignalingDTO(BaseDTO):
    call_id: str
    sender_id: str
    recipient_id: Optional[str] = None
    room_id: Optional[str] = None
    type: str  # 'offer', 'answer', 'ice_candidate', 'state_change', 'leave'
    sdp: Optional[str] = None
    candidate: Optional[Dict[str, Any]] = None
    call_state: Optional[CallState] = None
