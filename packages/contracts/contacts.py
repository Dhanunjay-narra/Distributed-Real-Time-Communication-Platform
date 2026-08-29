from typing import Optional, List
from .models import TimestampedModel, BaseDTO
from .users import UserProfileDTO

class AddContactRequest(BaseDTO):
    contact_user_id: str
    alias: Optional[str] = None

class ContactDTO(TimestampedModel):
    user_id: str
    contact_user_id: str
    alias: Optional[str] = None
    is_favorite: bool = False
    is_blocked: bool = False
    contact_profile: Optional[UserProfileDTO] = None
