import uuid, os, hashlib
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from packages.common.exceptions import NotFoundException, ValidationException, ForbiddenException
from packages.common.config import settings
from packages.contracts.media import MediaInitRequest, MediaInitResponse, MediaDTO
from .models import MediaFile

def _ensure_utc(dt: datetime) -> datetime:
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt or datetime.now(timezone.utc)

class MediaService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.max_file_size_bytes = 100 * 1024 * 1024  # 100MB limit
        self.blocked_extensions = {".exe", ".bat", ".sh", ".cmd", ".vbs", ".msi"}

    async def init_upload(self, user_id: str, req: MediaInitRequest) -> MediaInitResponse:
        _, ext = os.path.splitext(req.filename.lower())
        if ext in self.blocked_extensions:
            raise ValidationException(f"File extension '{ext}' is prohibited for security reasons")

        if req.file_size_bytes > self.max_file_size_bytes:
            raise ValidationException("File size exceeds 100MB platform limit")

        media_id = str(uuid.uuid4())
        chunk_size = 5 * 1024 * 1024  # 5MB chunks
        total_chunks = max(1, (req.file_size_bytes + chunk_size - 1) // chunk_size)

        upload_url = f"/api/v1/media/upload/chunk?media_id={media_id}"
        return MediaInitResponse(
            media_id=media_id,
            upload_url=upload_url,
            chunk_size=chunk_size,
            total_chunks=total_chunks
        )

    async def complete_upload(
        self,
        user_id: str,
        media_id: str,
        filename: str,
        content_type: str,
        file_size_bytes: int,
        duration: Optional[float] = None,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> MediaDTO:
        storage_key = f"media/{user_id}/{media_id}/{filename}"
        cdn_url = f"/storage/{storage_key}"
        thumb_url = f"/storage/{storage_key}_thumb.jpg" if content_type.startswith("image/") else None
        waveform = [12, 45, 89, 100, 60, 30, 80, 45] if content_type.startswith("audio/") else None

        media = MediaFile(
            id=media_id,
            user_id=user_id,
            filename=filename,
            content_type=content_type,
            file_size_bytes=file_size_bytes,
            storage_key=storage_key,
            cdn_url=cdn_url,
            thumbnail_url=thumb_url,
            media_category=content_type.split("/")[0],
            duration_seconds=duration,
            width=width,
            height=height,
            waveform_data=waveform,
            is_safe=True
        )
        self.db.add(media)
        await self.db.commit()
        await self.db.refresh(media)

        return MediaDTO(
            id=media.id,
            user_id=media.user_id,
            filename=media.filename,
            content_type=media.content_type,
            file_size_bytes=media.file_size_bytes,
            storage_key=media.storage_key,
            cdn_url=media.cdn_url,
            thumbnail_url=media.thumbnail_url,
            duration_seconds=media.duration_seconds,
            width=media.width,
            height=media.height,
            waveform_data=media.waveform_data,
            created_at=_ensure_utc(media.created_at),
            updated_at=_ensure_utc(media.created_at)
        )

    async def get_media(self, media_id: str) -> MediaDTO:
        stmt = select(MediaFile).where(MediaFile.id == media_id)
        res = await self.db.execute(stmt)
        media = res.scalar_one_or_none()
        if not media:
            raise NotFoundException("Media file not found")

        return MediaDTO(
            id=media.id,
            user_id=media.user_id,
            filename=media.filename,
            content_type=media.content_type,
            file_size_bytes=media.file_size_bytes,
            storage_key=media.storage_key,
            cdn_url=media.cdn_url,
            thumbnail_url=media.thumbnail_url,
            duration_seconds=media.duration_seconds,
            width=media.width,
            height=media.height,
            waveform_data=media.waveform_data,
            created_at=_ensure_utc(media.created_at),
            updated_at=_ensure_utc(media.created_at)
        )
