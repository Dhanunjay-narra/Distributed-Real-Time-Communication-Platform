"""WebRTC Voice/Video Signaling Mesh - Stream Checkpoint and High-Watermark Offset Manager.
"""
import time
from typing import Dict

class CallsStreamCheckpointer:
    def __init__(self):
        self.committed_offsets: Dict[str, int] = {}

    def commit_offset(self, partition: str, offset: int):
        self.committed_offsets[partition] = offset

    def get_last_offset(self, partition: str) -> int:
        return self.committed_offsets.get(partition, 0)
