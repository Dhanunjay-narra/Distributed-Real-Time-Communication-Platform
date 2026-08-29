import secrets, base64, hashlib, os
import bcrypt
from typing import Tuple

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def generate_random_token(length_bytes: int = 32) -> str:
    return secrets.token_urlsafe(length_bytes)

def generate_numeric_otp(digits: int = 6) -> str:
    return "".join(secrets.choice("0123456789") for _ in range(digits))

def sha256_hash(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def hmac_sha256(key: str, message: str) -> str:
    import hmac
    return hmac.new(key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()
