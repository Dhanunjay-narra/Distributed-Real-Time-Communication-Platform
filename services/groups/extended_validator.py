"""Hierarchical RBAC and Announcement Channels - Extended JSON Schema & Regex Validator.
"""
import re
from typing import Dict, Any, List

class GroupsExtendedValidator:
    def __init__(self):
        self.required_keys: List[str] = ["id", "timestamp"]

    def validate_schema(self, payload: Dict[str, Any]) -> bool:
        for k in self.required_keys:
            if k not in payload:
                return False
        return True

    def sanitize_sql_injection_patterns(self, text: str) -> str:
        dangerous_patterns = [r"--", r";", r"/\*", r"\*/", r"DROP\s+TABLE", r"UNION\s+SELECT"]
        cleaned = text
        for p in dangerous_patterns:
            cleaned = re.sub(p, "", cleaned, flags=re.IGNORECASE)
        return cleaned.strip()
