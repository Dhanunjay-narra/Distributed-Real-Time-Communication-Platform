from typing import Optional, Dict, Any
from .models import TimestampedModel, BaseDTO

class MediaDTO(TimestampedModel):
    user_id: str
    filename: str
    content_type: str
    file_size_bytes: int
    storage_key: str
    cdn_url: str
    thumbnail_url: Optional[str] = None
