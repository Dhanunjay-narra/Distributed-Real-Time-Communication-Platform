from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from packages.common.database import get_db_session
from packages.contracts.models import APIResponse
from packages.contracts.users import UpdateProfileRequest
from packages.security.jwt import decode_token
from .service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

@router.get("/me", response_model=APIResponse)
async def get_my_profile(authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = UserService(db)
    profile = await svc.get_profile(claims.sub)
    return APIResponse(data=profile.model_dump())

@router.put("/me", response_model=APIResponse)
async def update_my_profile(req: UpdateProfileRequest, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = UserService(db)
    profile = await svc.update_profile(claims.sub, req)
    return APIResponse(message="Profile updated", data=profile.model_dump())

@router.get("/search", response_model=APIResponse)
async def search_users(q: str = Query(..., min_length=1), authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    svc = UserService(db)
    results = await svc.search_users(q)
    return APIResponse(data=[u.model_dump() for u in results])

@router.get("/{user_id}", response_model=APIResponse)
async def get_user_profile(user_id: str, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    svc = UserService(db)
    profile = await svc.get_profile(user_id)
    return APIResponse(data=profile.model_dump())
