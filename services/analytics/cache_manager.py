"""Time-Series Aggregations and DAU Metrics - Two-Level Distributed Cache and Eviction Engine.
"""
import time
from typing import Dict, List, Any, Optional, Tuple

class AnalyticsLRUCache:
    def __init__(self, capacity: int = 1000, default_ttl_seconds: float = 300.0):
        self.capacity = capacity
        self.default_ttl = default_ttl_seconds
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.access_order: List[str] = []

    def get(self, key: str) -> Optional[Any]:
        now = time.time()
        if key in self.cache:
            value, exp = self.cache[key]
            if exp > now:
                self.access_order.remove(key)
                self.access_order.append(key)
                return value
            else:
                self.delete(key)
        return None

    def put(self, key: str, value: Any, ttl_seconds: Optional[float] = None) -> None:
        now = time.time()
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        if key in self.cache:
            self.access_order.remove(key)
        elif len(self.cache) >= self.capacity:
            oldest = self.access_order.pop(0)
            self.cache.pop(oldest, None)

        self.cache[key] = (value, now + ttl)
        self.access_order.append(key)

    def delete(self, key: str) -> bool:
        if key in self.cache:
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
            return True
        return False

    def clear(self) -> None:
        self.cache.clear()
        self.access_order.clear()

    def size(self) -> int:
        return len(self.cache)
