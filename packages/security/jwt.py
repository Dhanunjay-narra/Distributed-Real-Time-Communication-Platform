import uuid
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
    jti: Optional[str] = None
    exp: datetime
    iat: datetime

def create_access_token(
    user_id: str,
    device_id: str,
    username: Optional[str] = None,
    role: str = "user",
    expires_delta: Optional[timedelta] = None
) -> str:
    now = datetime.now(timezone.utc)
    expires = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": user_id,
        "device_id": device_id,
        "username": username,
        "role": role,
        "token_type": "access",
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": expires,
    }
    secret = getattr(settings, "SECRET_KEY", getattr(settings, "JWT_SECRET_KEY", "secret-key"))
    algo = getattr(settings, "ALGORITHM", getattr(settings, "JWT_ALGORITHM", "HS256"))
    return jwt.encode(payload, secret, algorithm=algo)

def create_refresh_token(
    user_id: str,
    device_id: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    now = datetime.now(timezone.utc)
    expires = now + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    payload = {
        "sub": user_id,
        "device_id": device_id,
        "token_type": "refresh",
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": expires,
    }
    secret = getattr(settings, "SECRET_KEY", getattr(settings, "JWT_SECRET_KEY", "secret-key"))
    algo = getattr(settings, "ALGORITHM", getattr(settings, "JWT_ALGORITHM", "HS256"))
    return jwt.encode(payload, secret, algorithm=algo)

def decode_token(token: str) -> TokenClaims:
    secret = getattr(settings, "SECRET_KEY", getattr(settings, "JWT_SECRET_KEY", "secret-key"))
    algo = getattr(settings, "ALGORITHM", getattr(settings, "JWT_ALGORITHM", "HS256"))
    try:
        return TokenClaims(**jwt.decode(token, secret, algorithms=[algo]))
    except Exception:
        raise UnauthorizedException("Invalid or expired token")
