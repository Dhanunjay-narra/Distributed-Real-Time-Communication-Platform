"""Infrastructure Drivers and Resilience Toolkit - Partition-Aware Key-Value Store.
"""
import time
from typing import Dict, List, Any, Optional

class CommonPartitionStore:
    def __init__(self, partition_id: str):
        self.partition_id = partition_id
        self.storage: Dict[str, Any] = {}
        self.metadata_index: Dict[str, float] = {}

    def put(self, key: str, value: Any):
        self.storage[key] = value
        self.metadata_index[key] = time.time()

    def get(self, key: str) -> Optional[Any]:
        return self.storage.get(key)

    def delete(self, key: str) -> bool:
        if key in self.storage:
            del self.storage[key]
            self.metadata_index.pop(key, None)
            return True
        return False

    def list_keys(self) -> List[str]:
        return list(self.storage.keys())

    def get_stats(self) -> Dict[str, Any]:
        return {
            "partition_id": self.partition_id,
            "key_count": len(self.storage),
            "service": "common"
        }
