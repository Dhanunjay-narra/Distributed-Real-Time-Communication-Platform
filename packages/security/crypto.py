import secrets
import base64
import hashlib
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def generate_secure_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)

def generate_otp(digits: int = 6) -> str:
    return "".join(secrets.choice("0123456789") for _ in range(digits))

def encrypt_payload(data: str, secret_key: str) -> str:
    key = hashlib.sha256(secret_key.encode()).digest()
    data_bytes = data.encode()
    cipher_bytes = bytearray(b ^ key[i % len(key)] for i, b in enumerate(data_bytes))
    return base64.urlsafe_b64encode(cipher_bytes).decode()

def decrypt_payload(encrypted_data: str, secret_key: str) -> str:
    key = hashlib.sha256(secret_key.encode()).digest()
    cipher_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
    data_bytes = bytearray(b ^ key[i % len(key)] for i, b in enumerate(cipher_bytes))
    return data_bytes.decode()
