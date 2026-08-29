from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from packages.common.database import get_db_session
from packages.contracts.models import APIResponse
from packages.contracts.contacts import AddContactRequest
from packages.security.jwt import decode_token
from .service import ContactService

router = APIRouter(prefix="/api/v1/contacts", tags=["Contacts"])

@router.get("", response_model=APIResponse)
async def list_contacts(authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = ContactService(db)
    contacts = await svc.list_contacts(claims.sub)
    return APIResponse(data=[c.model_dump() for c in contacts])

@router.post("", response_model=APIResponse)
async def add_contact(req: AddContactRequest, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = ContactService(db)
    contact = await svc.add_contact(claims.sub, req)
    return APIResponse(message="Contact added", data=contact.model_dump())

@router.delete("/{contact_user_id}", response_model=APIResponse)
async def remove_contact(contact_user_id: str, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = ContactService(db)
    await svc.remove_contact(claims.sub, contact_user_id)
    return APIResponse(message="Contact removed")

@router.post("/{contact_user_id}/favorite", response_model=APIResponse)
async def toggle_favorite(contact_user_id: str, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    claims = decode_token(authorization.replace("Bearer ", ""))
    svc = ContactService(db)
    is_fav = await svc.toggle_favorite(claims.sub, contact_user_id)
    return APIResponse(data={"is_favorite": is_fav})
