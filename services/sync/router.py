from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from packages.common.database import get_db_session
from packages.contracts.models import APIResponse
from packages.contracts.sync import SyncPullRequest
from packages.security.jwt import decode_token
from .service import SyncService

router = APIRouter(prefix="/api/v1/sync", tags=["Multi-Device Sync"])

@router.post("/pull", response_model=APIResponse)
async def pull_sync(req: SyncPullRequest, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = SyncService(db)
    delta = await svc.pull_deltas(claims.sub, req)
    return APIResponse(data=delta.model_dump())
