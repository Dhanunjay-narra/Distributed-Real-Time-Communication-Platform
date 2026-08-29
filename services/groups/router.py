from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from packages.common.database import get_db_session
from packages.contracts.models import APIResponse
from packages.contracts.groups import CreateGroupRequest, UpdateGroupMemberRoleRequest
from packages.security.jwt import decode_token
from .service import GroupService

router = APIRouter(prefix="/api/v1/groups", tags=["Groups"])

@router.post("", response_model=APIResponse)
async def create_group(req: CreateGroupRequest, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = GroupService(db)
    group = await svc.create_group(claims.sub, req)
    return APIResponse(message="Group created", data=group.model_dump())

@router.get("/{group_id}", response_model=APIResponse)
async def get_group(group_id: str, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = GroupService(db)
    group = await svc.get_group(group_id, claims.sub)
    return APIResponse(data=group.model_dump())

@router.post("/{group_id}/members/{user_id}", response_model=APIResponse)
async def add_member(group_id: str, user_id: str, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = GroupService(db)
    await svc.add_member(group_id, claims.sub, user_id)
    return APIResponse(message="Member added")

@router.delete("/{group_id}/members/{user_id}", response_model=APIResponse)
async def remove_member(group_id: str, user_id: str, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = GroupService(db)
    await svc.remove_member(group_id, claims.sub, user_id)
    return APIResponse(message="Member removed")

@router.put("/{group_id}/members/{user_id}/role", response_model=APIResponse)
async def update_role(group_id: str, user_id: str, req: UpdateGroupMemberRoleRequest, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = GroupService(db)
    await svc.update_member_role(group_id, claims.sub, user_id, req.new_role)
    return APIResponse(message="Member role updated")

@router.post("/join/{invite_code}", response_model=APIResponse)
async def join_group_invite(invite_code: str, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = GroupService(db)
    group = await svc.join_by_invite(invite_code, claims.sub)
    return APIResponse(message="Joined group", data=group.model_dump())
