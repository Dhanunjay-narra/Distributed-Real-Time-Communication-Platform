import re
from typing import Optional

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?[1-9]\d{1,14}$")
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_.-]{3,30}$")

def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email.strip())) if email else False

def is_valid_phone(phone: str) -> bool:
    return bool(PHONE_REGEX.match(phone.strip())) if phone else False

def is_valid_username(username: str) -> bool:
    return bool(USERNAME_REGEX.match(username.strip())) if username else False

def sanitize_text(text: str) -> str:
    return text.replace("<script>", "").replace("</script>", "").strip()
