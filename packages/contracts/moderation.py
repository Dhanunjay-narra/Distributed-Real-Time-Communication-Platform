from typing import Optional, List
from enum import Enum
from .models import TimestampedModel, BaseDTO

class ReportReason(str, Enum):
    SPAM = "spam"
    HARASSMENT = "harassment"
    ABUSE = "abuse"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    OTHER = "other"

class CreateReportRequest(BaseDTO):
    reported_user_id: str
    message_id: Optional[str] = None
    conversation_id: Optional[str] = None
    reason: ReportReason = ReportReason.SPAM
    description: Optional[str] = None

class SanctionType(str, Enum):
    WARNING = "warning"
    TEMPORARY_BAN = "temporary_ban"
    PERMANENT_BAN = "permanent_ban"
    MUTE = "mute"

class ApplySanctionRequest(BaseDTO):
    user_id: str
    sanction_type: SanctionType
    duration_hours: Optional[int] = None
    reason: str
