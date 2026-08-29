from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from .models import BaseDTO, TimestampedModel

class RegisterRequest(BaseDTO):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    username: str = Field(..., min_length=3, max_length=30)
    display_name: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=8)
    device_name: Optional[str] = "Web Browser"
    device_type: Optional[str] = "web"

class LoginRequest(BaseDTO):
    identifier: str
    password: str
    device_id: Optional[str] = None
    device_name: Optional[str] = "Web Browser"
    device_type: Optional[str] = "web"

class OTPRequest(BaseDTO):
    target: str
    channel: str = "email"

class OTPVerifyRequest(BaseDTO):
    target: str
    code: str
    device_name: Optional[str] = "Web Browser"
    device_type: Optional[str] = "web"

class TokenResponse(BaseDTO):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    device_id: str

class RefreshTokenRequest(BaseDTO):
    refresh_token: str
    device_id: str

class SessionInfo(TimestampedModel):
    user_id: str
    device_id: str
    device_name: str
    device_type: str
    ip_address: Optional[str] = None
    last_active: datetime
    is_current: bool = False
