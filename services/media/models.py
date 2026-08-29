import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Float, JSON
from packages.common.database import Base

class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    storage_key = Column(String(500), nullable=False, unique=True)
    cdn_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    media_category = Column(String(50), default="image")  # 'image', 'video', 'audio', 'document'
    duration_seconds = Column(Float, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    waveform_data = Column(JSON, nullable=True)
    is_safe = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
