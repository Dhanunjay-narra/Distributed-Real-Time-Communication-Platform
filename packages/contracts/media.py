from typing import Optional, Dict, Any
from .models import TimestampedModel, BaseDTO

class MediaInitRequest(BaseDTO):
    filename: str
    content_type: str
    file_size_bytes: int
    media_category: str = "image"

class MediaInitResponse(BaseDTO):
    media_id: str
    upload_url: str
    chunk_size: int
    total_chunks: int

class MediaDTO(TimestampedModel):
    user_id: str
    filename: str
    content_type: str
    file_size_bytes: int
    storage_key: str
    cdn_url: str
    thumbnail_url: Optional[str] = None
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    waveform_data: Optional[list] = None
