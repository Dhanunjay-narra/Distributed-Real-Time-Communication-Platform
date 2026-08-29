"""User Profiles and Presence Status - Read/Write Replica Connection Split Pool.
"""
from typing import List, Dict, Any, Optional

class UsersReplicaSplitPool:
    def __init__(self, primary_url: str, replica_urls: List[str]):
        self.primary_url = primary_url
        self.replica_urls = replica_urls
        self._read_index = 0

    def get_writer_endpoint(self) -> str:
        return self.primary_url

    def get_reader_endpoint(self) -> str:
        if not self.replica_urls:
            return self.primary_url
        endpoint = self.replica_urls[self._read_index % len(self.replica_urls)]
        self._read_index += 1
        return endpoint

    def get_pool_health(self) -> Dict[str, Any]:
        return {
            "service": "users",
            "primary_available": True,
            "replica_count": len(self.replica_urls)
        }
