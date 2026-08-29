"""Hierarchical RBAC and Announcement Channels - HKDF RFC 5869 Key Derivation Function.
"""
import hmac, hashlib
from typing import Tuple

class GroupsHKDFKeyDerivation:
    @staticmethod
    def extract_and_expand(salt: bytes, ikm: bytes, info: bytes, length: int = 32) -> bytes:
        if not salt:
            salt = b"\x00" * 32
        prk = hmac.new(salt, ikm, hashlib.sha256).digest()
        
        okm = b""
        t = b""
        i = 1
        while len(okm) < length:
            t = hmac.new(prk, t + info + bytes([i]), hashlib.sha256).digest()
            okm += t
            i += 1
        return okm[:length]
