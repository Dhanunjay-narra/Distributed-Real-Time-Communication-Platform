import json, time, asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Any
from packages.common.redis_client import get_redis_client
from packages.common.logger import get_logger
from packages.contracts.presence import PresenceStatus, PresenceHeartbeat, TypingIndicatorDTO

logger = get_logger("presence-mesh")

class PresenceMeshService:
    def __init__(self):
        self._local_presence: Dict[str, Dict[str, Any]] = {}
        self._local_typing: Dict[str, Dict[str, float]] = {}
        self._typing_timeout_seconds = 5.0
        self._presence_ttl_seconds = 45

    async def heartbeat(self, heartbeat: PresenceHeartbeat) -> None:
        redis = await get_redis_client()
        now = time.time()
        key = f"presence:{heartbeat.user_id}:{heartbeat.device_id}"
        val = {
            "user_id": heartbeat.user_id,
            "device_id": heartbeat.device_id,
            "status": heartbeat.status.value,
            "custom_status": heartbeat.custom_status,
            "timestamp": now
        }
        await redis.set(key, val, expire_seconds=self._presence_ttl_seconds)

        channel = f"presence:user:{heartbeat.user_id}"
        await redis.publish(channel, val)

        if heartbeat.user_id not in self._local_presence:
            self._local_presence[heartbeat.user_id] = {"status": heartbeat.status.value, "devices": set(), "last_heartbeat": now}
        self._local_presence[heartbeat.user_id]["status"] = heartbeat.status.value
        self._local_presence[heartbeat.user_id]["last_heartbeat"] = now
        self._local_presence[heartbeat.user_id]["devices"].add(heartbeat.device_id)

    async def get_presence(self, user_id: str) -> Dict[str, Any]:
        redis = await get_redis_client()
        now = time.time()
        
        if user_id in self._local_presence:
            rec = self._local_presence[user_id]
            if now - rec["last_heartbeat"] < self._presence_ttl_seconds:
                return {"user_id": user_id, "status": rec["status"], "is_online": rec["status"] != "OFFLINE"}

        return {"user_id": user_id, "status": "OFFLINE", "is_online": False}

    async def set_offline(self, user_id: str, device_id: str) -> None:
        redis = await get_redis_client()
        key = f"presence:{user_id}:{device_id}"
        await redis.delete(key)
        
        if user_id in self._local_presence:
            self._local_presence[user_id]["devices"].discard(device_id)
            if not self._local_presence[user_id]["devices"]:
                self._local_presence[user_id]["status"] = "OFFLINE"

        channel = f"presence:user:{user_id}"
        await redis.publish(channel, {"user_id": user_id, "device_id": device_id, "status": "OFFLINE", "timestamp": time.time()})

    async def set_typing(self, conversation_id: str, user_id: str, is_typing: bool) -> List[str]:
        now = time.time()
        if conversation_id not in self._local_typing:
            self._local_typing[conversation_id] = {}

        if is_typing:
            self._local_typing[conversation_id][user_id] = now
        else:
            self._local_typing[conversation_id].pop(user_id, None)

        active_typers = []
        for uid, t in list(self._local_typing[conversation_id].items()):
            if now - t <= self._typing_timeout_seconds:
                active_typers.append(uid)
            else:
                self._local_typing[conversation_id].pop(uid, None)

        redis = await get_redis_client()
        channel = f"typing:conv:{conversation_id}"
        await redis.publish(channel, {"conversation_id": conversation_id, "user_id": user_id, "is_typing": is_typing, "active_typers": active_typers})
        return active_typers

    async def get_active_typers(self, conversation_id: str) -> List[str]:
        now = time.time()
        active = []
        if conversation_id in self._local_typing:
            for uid, t in list(self._local_typing[conversation_id].items()):
                if now - t <= self._typing_timeout_seconds:
                    active.append(uid)
                else:
                    self._local_typing[conversation_id].pop(uid, None)
        return active
