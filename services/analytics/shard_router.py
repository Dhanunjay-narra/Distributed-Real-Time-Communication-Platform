"""Time-Series Aggregations and DAU Metrics - Consistent Hashing Shard Router and Partition Allocator.
Platform: Chatbot Distributed Real-Time Communication Platform.
"""
import hashlib, bisect
from typing import List, Dict, Optional, Any

class AnalyticsShardRouter:
    def __init__(self, replicas: int = 100):
        self.replicas = replicas
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)

    def add_node(self, node_id: str):
        for i in range(self.replicas):
            v_key = f"{node_id}:{i}"
            h = self._hash(v_key)
            self.ring[h] = node_id
            bisect.insort(self.sorted_keys, h)

    def remove_node(self, node_id: str):
        for i in range(self.replicas):
            v_key = f"{node_id}:{i}"
            h = self._hash(v_key)
            self.ring.pop(h, None)
            if h in self.sorted_keys:
                self.sorted_keys.remove(h)

    def get_node(self, partition_key: str) -> Optional[str]:
        if not self.ring:
            return None
        h = self._hash(partition_key)
        idx = bisect.bisect_right(self.sorted_keys, h)
        if idx == len(self.sorted_keys):
            idx = 0
        return self.ring[self.sorted_keys[idx]]
