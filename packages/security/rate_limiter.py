import time
from typing import Optional
from packages.common.exceptions import RateLimitException

class DistributedRateLimiter:
    def __init__(self, redis_manager=None):
        self.redis_manager = redis_manager
        self._local_counts = {}

    async def check_rate_limit(self, identifier: str, limit: int = 60, window_seconds: int = 60) -> bool:
        now = time.time()
        start = now - window_seconds
        records = [t for t in self._local_counts.get(identifier, []) if t > start]
        if len(records) >= limit:
            raise RateLimitException(retry_after=window_seconds)
        records.append(now)
        self._local_counts[identifier] = records
        return True
