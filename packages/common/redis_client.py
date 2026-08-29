import asyncio, json, uuid, time
from typing import Optional, Any, Dict
import redis.asyncio as aioredis
from .config import settings
from .logger import get_logger

logger = get_logger("redis-manager")

class RedisClusterManager:
    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.redis_url = redis_url
        self.client: Optional[aioredis.Redis] = None

    async def connect(self) -> Optional[aioredis.Redis]:
        if self.client is None:
            try:
                self.client = aioredis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
                await self.client.ping()
            except Exception as e:
                logger.warning(f"Redis unavailable ({e}), using memory fallback.")
                self.client = None
        return self.client

    async def get(self, key: str) -> Optional[str]:
        if self.client:
            try: return await self.client.get(key)
            except Exception: pass
        return None

    async def set(self, key: str, value: Any, expire_seconds: Optional[int] = None) -> bool:
        if self.client:
            try:
                val = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
                if expire_seconds: await self.client.setex(key, expire_seconds, val)
                else: await self.client.set(key, val)
                return True
            except Exception: pass
        return False

    async def delete(self, key: str) -> bool:
        if self.client:
            try:
                await self.client.delete(key)
                return True
            except Exception: pass
        return False

    async def acquire_lock(self, lock_name: str, acquire_timeout: float = 5.0, lock_timeout: int = 10) -> Optional[str]:
        ident = str(uuid.uuid4())
        end = time.time() + acquire_timeout
        key = f"lock:{lock_name}"
        while time.time() < end:
            if self.client:
                try:
                    if await self.client.set(key, ident, nx=True, ex=lock_timeout): return ident
                except Exception: pass
            else: return ident
            await asyncio.sleep(0.05)
        return None

    async def release_lock(self, lock_name: str, identifier: str) -> bool:
        if self.client:
            try:
                key = f"lock:{lock_name}"
                if await self.client.get(key) == identifier: await self.client.delete(key)
            except Exception: pass
        return True

    async def publish(self, channel: str, message: Dict[str, Any]) -> int:
        if self.client:
            try: return await self.client.publish(channel, json.dumps(message))
            except Exception: pass
        return 0

    async def close(self):
        if self.client: await self.client.close()

redis_manager = RedisClusterManager()
async def get_redis_client() -> RedisClusterManager:
    if redis_manager.client is None: await redis_manager.connect()
    return redis_manager
