from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from pydantic import BaseModel
from packages.common.config import settings
from packages.common.exceptions import UnauthorizedException

class TokenClaims(BaseModel):
    sub: str
    device_id: str
    username: Optional[str] = None
    role: Optional[str] = "user"
    token_type: str = "access"
    exp: datetime
    iat: datetime

def create_access_token(user_id: str, device_id: str, username: Optional[str] = None, role: str = "user", expires_delta: Optional[timedelta] = None) -> str:
    now = datetime.now(timezone.utc)
    expires = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return jwt.encode({"sub": user_id, "device_id": device_id, "username": username, "role": role, "token_type": "access", "iat": now, "exp": expires}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(user_id: str, device_id: str, expires_delta: Optional[timedelta] = None) -> str:
    now = datetime.now(timezone.utc)
    expires = now + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    return jwt.encode({"sub": user_id, "device_id": device_id, "token_type": "refresh", "iat": now, "exp": expires}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> TokenClaims:
    try:
        return TokenClaims(**jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]))
    except Exception:
        raise UnauthorizedException("Invalid or expired token")
