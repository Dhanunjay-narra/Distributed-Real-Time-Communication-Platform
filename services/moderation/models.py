import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, Boolean
from packages.common.database import Base

class ContentReport(Base):
    __tablename__ = "content_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    reporter_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    reported_user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    message_id = Column(String(36), nullable=True)
    conversation_id = Column(String(36), nullable=True)
    reason = Column(String(50), default="spam")
    description = Column(Text, nullable=True)
    status = Column(String(30), default="PENDING")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class UserSanction(Base):
    __tablename__ = "user_sanctions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    sanction_type = Column(String(50), nullable=False)
    reason = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
