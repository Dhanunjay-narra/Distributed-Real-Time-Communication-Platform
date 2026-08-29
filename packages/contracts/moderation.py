from typing import Optional
from enum import Enum
from .models import TimestampedModel, BaseDTO

class ReportReason(str, Enum):
    SPAM = "spam"
    HARASSMENT = "harassment"
    ABUSE = "abuse"
    OTHER = "other"

class CreateReportRequest(BaseDTO):
    reported_user_id: str
    message_id: Optional[str] = None
    conversation_id: Optional[str] = None
    reason: ReportReason = ReportReason.SPAM
    description: Optional[str] = None
