from typing import List, Dict, Optional
from .models import BaseDTO
from .messages import MessageDTO

class SyncPullRequest(BaseDTO):
    device_id: str
    since_sequence: int = 0
    conversation_cursors: Dict[str, int] = {}
    limit: int = 50

class SyncDeltaResponse(BaseDTO):
    latest_sequence: int
    messages: List[MessageDTO] = []
    read_states: Dict[str, int] = {}
    deleted_message_ids: List[str] = []
    has_more: bool = False
