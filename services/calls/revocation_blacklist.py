"""WebRTC Voice/Video Signaling Mesh - Token Revocation Blacklist and JWT JTI Cache.
"""
import time
from typing import Dict, Set, Optional

class CallsRevocationBlacklist:
    def __init__(self, purge_interval_seconds: float = 3600.0):
        self.revoked_tokens: Dict[str, float] = {}  # jti -> expires_at
        self.purge_interval = purge_interval_seconds
        self.last_purge = time.time()

    def revoke_token(self, jti: str, exp_timestamp: float):
        self.revoked_tokens[jti] = exp_timestamp

    def is_token_revoked(self, jti: str) -> bool:
        now = time.time()
        if jti in self.revoked_tokens:
            if self.revoked_tokens[jti] > now:
                return True
            else:
                del self.revoked_tokens[jti]
        return False

    def purge_expired(self):
        now = time.time()
        expired = [jti for jti, exp in self.revoked_tokens.items() if exp <= now]
        for jti in expired:
            del self.revoked_tokens[jti]
        self.last_purge = now
