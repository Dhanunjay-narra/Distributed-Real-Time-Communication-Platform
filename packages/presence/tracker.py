from dataclasses import dataclass
from typing import Dict
import time

@dataclass
class PresenceTracker:
    ttl_seconds: float = 30.0

    def __post_init__(self):
        self._user_heartbeats: Dict[str, float] = {}

    def heartbeat(self, user_id: str):
        self._user_heartbeats[user_id] = time.time()

    def is_online(self, user_id: str) -> bool:
        last = self._user_heartbeats.get(user_id)
        if not last:
            return False
        return (time.time() - last) <= self.ttl_seconds
