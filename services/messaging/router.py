from fastapi import APIRouter, Depends, Header, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from packages.common.database import get_db_session
from packages.contracts.models import APIResponse
from packages.contracts.messages import SendMessageRequest, EditMessageRequest, MessageReactionRequest
from packages.security.jwt import decode_token
from .service import MessagingService

router = APIRouter(prefix="/api/v1/messages", tags=["Messaging"])

@router.post("", response_model=APIResponse)
async def send_message(req: SendMessageRequest, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = MessagingService(db)
    msg = await svc.send_message(claims.sub, req, sender_device_id=claims.device_id)
    return APIResponse(message="Message sent", data=msg.model_dump())

@router.get("/conversation/{conversation_id}", response_model=APIResponse)
async def list_messages(conversation_id: str, limit: int = Query(default=50, le=100), before_seq: Optional[int] = Query(default=None), authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    decode_token(authorization.replace("Bearer ", ""))
    svc = MessagingService(db)
    msgs = await svc.list_messages(conversation_id, limit=limit, before_sequence=before_seq)
    return APIResponse(data=[m.model_dump() for m in msgs])

@router.put("/{message_id}", response_model=APIResponse)
async def edit_message(message_id: str, req: EditMessageRequest, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = MessagingService(db)
    msg = await svc.edit_message(message_id, claims.sub, req)
    return APIResponse(message="Message edited", data=msg.model_dump())

@router.delete("/{message_id}", response_model=APIResponse)
async def delete_for_everyone(message_id: str, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = MessagingService(db)
    await svc.delete_for_everyone(message_id, claims.sub)
    return APIResponse(message="Message deleted for everyone")

@router.post("/{message_id}/react", response_model=APIResponse)
async def react_to_message(message_id: str, req: MessageReactionRequest, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = MessagingService(db)
    reactions = await svc.toggle_reaction(message_id, claims.sub, req.emoji)
    return APIResponse(data=reactions)

@router.post("/{message_id}/read", response_model=APIResponse)
async def mark_read(message_id: str, conversation_id: str = Query(...), authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = MessagingService(db)
    await svc.mark_as_read(conversation_id, claims.sub, message_id)
    return APIResponse(message="Marked as read")
