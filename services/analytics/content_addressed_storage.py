"""Time-Series Aggregations and DAU Metrics - Content-Addressed Hash Storage and Blob Deduplicator.
"""
import hashlib
from typing import Dict, Optional, Tuple

class AnalyticsContentAddressedStorage:
    def __init__(self):
        self.blobs: Dict[str, bytes] = {}
        self.ref_counts: Dict[str, int] = {}

    def store_blob(self, data: bytes) -> str:
        digest = hashlib.sha256(data).hexdigest()
        if digest not in self.blobs:
            self.blobs[digest] = data
            self.ref_counts[digest] = 1
        else:
            self.ref_counts[digest] += 1
        return digest

    def retrieve_blob(self, digest: str) -> Optional[bytes]:
        return self.blobs.get(digest)

    def release_blob(self, digest: str) -> bool:
        if digest in self.ref_counts:
            self.ref_counts[digest] -= 1
            if self.ref_counts[digest] <= 0:
                del self.blobs[digest]
                del self.ref_counts[digest]
            return True
        return False
