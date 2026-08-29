from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from packages.common.exceptions import NotFoundException, ConflictException, ValidationException
from services.auth.models import User
from services.users.models import Contact
from services.users.service import UserService
from packages.contracts.contacts import ContactDTO, AddContactRequest

def _ensure_utc(dt: datetime) -> datetime:
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt or datetime.now(timezone.utc)

class ContactService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_svc = UserService(db)

    async def add_contact(self, user_id: str, req: AddContactRequest) -> ContactDTO:
        if user_id == req.contact_user_id:
            raise ValidationException("Cannot add yourself as a contact")

        # Verify target user exists
        stmt = select(User).where(User.id == req.contact_user_id)
        res = await self.db.execute(stmt)
        contact_user = res.scalar_one_or_none()
        if not contact_user:
            raise NotFoundException("User not found")

        # Check existing contact
        stmt = select(Contact).where(and_(Contact.user_id == user_id, Contact.contact_user_id == req.contact_user_id))
        res = await self.db.execute(stmt)
        existing = res.scalar_one_or_none()
        if existing:
            raise ConflictException("User is already in your contacts")

        contact = Contact(
            user_id=user_id,
            contact_user_id=req.contact_user_id,
            alias=req.alias,
            is_favorite=False
        )
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)

        profile = await self.user_svc.get_profile(contact.contact_user_id)
        return ContactDTO(
            id=contact.id,
            user_id=contact.user_id,
            contact_user_id=contact.contact_user_id,
            alias=contact.alias,
            is_favorite=contact.is_favorite,
            contact_profile=profile,
            created_at=_ensure_utc(contact.created_at),
            updated_at=_ensure_utc(contact.created_at)
        )

    async def list_contacts(self, user_id: str) -> List[ContactDTO]:
        stmt = select(Contact).where(Contact.user_id == user_id).order_by(Contact.is_favorite.desc(), Contact.created_at.asc())
        res = await self.db.execute(stmt)
        contacts = res.scalars().all()

        dtos = []
        for c in contacts:
            profile = await self.user_svc.get_profile(c.contact_user_id)
            dtos.append(ContactDTO(
                id=c.id,
                user_id=c.user_id,
                contact_user_id=c.contact_user_id,
                alias=c.alias,
                is_favorite=c.is_favorite,
                contact_profile=profile,
                created_at=_ensure_utc(c.created_at),
                updated_at=_ensure_utc(c.created_at)
            ))
        return dtos

    async def remove_contact(self, user_id: str, contact_user_id: str) -> bool:
        stmt = delete(Contact).where(and_(Contact.user_id == user_id, Contact.contact_user_id == contact_user_id))
        await self.db.execute(stmt)
        await self.db.commit()
        return True

    async def toggle_favorite(self, user_id: str, contact_user_id: str) -> bool:
        stmt = select(Contact).where(and_(Contact.user_id == user_id, Contact.contact_user_id == contact_user_id))
        res = await self.db.execute(stmt)
        contact = res.scalar_one_or_none()
        if not contact:
            raise NotFoundException("Contact not found")
        contact.is_favorite = not contact.is_favorite
        await self.db.commit()
        return contact.is_favorite
