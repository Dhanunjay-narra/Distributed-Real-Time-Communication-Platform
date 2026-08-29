"""Idempotent Monotonic Real-Time Messaging - Input Sanitization and Domain Validators.
"""
import re
from typing import Dict, Any, List, Optional
from packages.common.exceptions import ValidationException

class MessagingValidator:
    @staticmethod
    def validate_payload(data: Dict[str, Any]) -> bool:
        if not isinstance(data, dict):
            raise ValidationException("Payload must be a dictionary object")
        return True

    @staticmethod
    def sanitize_field(field_value: str) -> str:
        if not isinstance(field_value, str):
            return str(field_value)
        cleaned = re.sub(r"[<>"'%;()&+]", "", field_value)
        return cleaned.strip()
