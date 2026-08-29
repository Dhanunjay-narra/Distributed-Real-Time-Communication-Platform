from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from packages.common.database import get_db_session
from packages.contracts.models import APIResponse
from packages.security.jwt import decode_token
from .service import PrivacyService

router = APIRouter(prefix="/api/v1/privacy", tags=["Privacy"])

@router.post("/block/{target_user_id}", response_model=APIResponse)
async def block_user(target_user_id: str, reason: str = Query(default=None), authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = PrivacyService(db)
    await svc.block_user(claims.sub, target_user_id, reason)
    return APIResponse(message="User blocked successfully")

@router.delete("/block/{target_user_id}", response_model=APIResponse)
async def unblock_user(target_user_id: str, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = PrivacyService(db)
    await svc.unblock_user(claims.sub, target_user_id)
    return APIResponse(message="User unblocked successfully")

@router.get("/blocked", response_model=APIResponse)
async def list_blocked(authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = PrivacyService(db)
    blocked_ids = await svc.list_blocked_users(claims.sub)
    return APIResponse(data=blocked_ids)
