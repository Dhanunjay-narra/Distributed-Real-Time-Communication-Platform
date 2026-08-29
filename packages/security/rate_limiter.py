import time
from typing import Dict, List
from packages.common.redis_client import get_redis_client
from packages.common.exceptions import RateLimitExceededException

class DistributedRateLimiter:
    def __init__(self):
        self._memory_windows: Dict[str, List[float]] = {}

    async def check_rate_limit(self, identifier: str, limit: int = 100, window_seconds: int = 60) -> bool:
        redis = await get_redis_client()
        now = time.time()
        key = f"rate:{identifier}"

        # If Redis is active, sliding window via sorted set or counter
        if redis.client:
            try:
                current = await redis.client.incr(key)
                if current == 1:
                    await redis.client.expire(key, window_seconds)
                if current > limit:
                    raise RateLimitExceededException(retry_after_seconds=window_seconds)
                return True
            except RateLimitExceededException:
                raise
            except Exception:
                pass

        # In-memory sliding log fallback
        timestamps = self._memory_windows.get(identifier, [])
        timestamps = [t for t in timestamps if now - t < window_seconds]
        if len(timestamps) >= limit:
            self._memory_windows[identifier] = timestamps
            raise RateLimitExceededException(retry_after_seconds=int(window_seconds - (now - timestamps[0])))

        timestamps.append(now)
        self._memory_windows[identifier] = timestamps
        return True
