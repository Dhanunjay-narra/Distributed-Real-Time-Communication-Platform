from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from packages.common.database import get_db_session
from packages.contracts.models import APIResponse
from packages.contracts.conversations import CreateConversationRequest
from packages.security.jwt import decode_token
from .service import ConversationService

router = APIRouter(prefix="/api/v1/conversations", tags=["Conversations"])

@router.get("", response_model=APIResponse)
async def list_conversations(authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = ConversationService(db)
    convs = await svc.list_user_conversations(claims.sub)
    return APIResponse(data=[c.model_dump() for c in convs])

@router.post("/direct/{recipient_id}", response_model=APIResponse)
async def get_or_create_direct(recipient_id: str, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = ConversationService(db)
    conv = await svc.create_or_get_direct(claims.sub, recipient_id)
    return APIResponse(data=conv.model_dump())

@router.get("/{conversation_id}", response_model=APIResponse)
async def get_conversation(conversation_id: str, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = ConversationService(db)
    conv = await svc.get_conversation(conversation_id, claims.sub)
    return APIResponse(data=conv.model_dump())

@router.post("/{conversation_id}/pin", response_model=APIResponse)
async def toggle_pin(conversation_id: str, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = ConversationService(db)
    is_pinned = await svc.toggle_pin(conversation_id, claims.sub)
    return APIResponse(data={"is_pinned": is_pinned})

@router.post("/{conversation_id}/mute", response_model=APIResponse)
async def toggle_mute(conversation_id: str, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = ConversationService(db)
    is_muted = await svc.toggle_mute(conversation_id, claims.sub)
    return APIResponse(data={"is_muted": is_muted})
