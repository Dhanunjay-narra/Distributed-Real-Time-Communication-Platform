from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from packages.common.database import get_db_session
from packages.contracts.models import APIResponse
from packages.contracts.media import MediaInitRequest
from packages.security.jwt import decode_token
from .service import MediaService

router = APIRouter(prefix="/api/v1/media", tags=["Media"])

@router.post("/init", response_model=APIResponse)
async def init_media_upload(req: MediaInitRequest, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = MediaService(db)
    init_res = await svc.init_upload(claims.sub, req)
    return APIResponse(message="Upload initialized", data=init_res.model_dump())

@router.get("/{media_id}", response_model=APIResponse)
async def get_media(media_id: str, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    decode_token(authorization.replace("Bearer ", ""))
    svc = MediaService(db)
    media = await svc.get_media(media_id)
    return APIResponse(data=media.model_dump())
