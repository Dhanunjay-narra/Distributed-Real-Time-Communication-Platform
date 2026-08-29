"""WebRTC Voice/Video Signaling Mesh - In-Memory Session and Token Cache.
"""
import time
from typing import Dict, Any, Optional, List

class CallsSessionCache:
    def __init__(self, ttl_seconds: float = 3600.0):
        self.ttl = ttl_seconds
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def store_session(self, session_id: str, user_id: str, device_id: str, metadata: Optional[Dict[str, Any]] = None):
        self.sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "device_id": device_id,
            "created_at": time.time(),
            "expires_at": time.time() + self.ttl,
            "metadata": metadata or {}
        }

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        now = time.time()
        session = self.sessions.get(session_id)
        if session and session["expires_at"] > now:
            return session
        elif session:
            del self.sessions[session_id]
        return None

    def invalidate_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
