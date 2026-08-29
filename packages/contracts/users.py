from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from .models import TimestampedModel, BaseDTO

class UserProfileDTO(TimestampedModel):
    username: str
    display_name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    about: Optional[str] = "Hey there! I am using Chatbot."
    bio: Optional[str] = None
    is_verified: bool = False
    presence_status: str = "OFFLINE"
    last_seen: Optional[datetime] = None

class UpdateProfileRequest(BaseDTO):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    about: Optional[str] = None
    bio: Optional[str] = None

class UserPreferencesDTO(BaseDTO):
    theme: str = "system"
    language: str = "en"
    notifications_enabled: bool = True
    sound_enabled: bool = True
    read_receipts_enabled: bool = True
    typing_indicator_enabled: bool = True
