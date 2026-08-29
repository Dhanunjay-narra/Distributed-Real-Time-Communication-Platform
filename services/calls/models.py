import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float
from packages.common.database import Base

class CallSession(Base):
    __tablename__ = "call_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    caller_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    recipient_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    room_id = Column(String(100), nullable=True, index=True)
    call_type = Column(String(20), default="voice")  # 'voice', 'video'
    call_state = Column(String(30), default="initiated")  # 'initiated', 'ringing', 'connected', 'ended', 'rejected', 'missed'
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    connected_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, default=0.0)
