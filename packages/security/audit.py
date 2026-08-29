import hashlib, time
from typing import List, Dict, Any

class ImmutableAuditLog:
    def __init__(self):
        self.entries: List[Dict[str, Any]] = []
        self.last_hash = "GENESIS_BLOCK_00000000000000000000000000000000000000000000000000000000"

    def record_action(self, actor_id: str, action: str, resource: str, metadata: Dict[str, Any] = None) -> str:
        timestamp = time.time()
        record_raw = f"{self.last_hash}|{actor_id}|{action}|{resource}|{timestamp}|{metadata or {}}"
        digest = hashlib.sha256(record_raw.encode("utf-8")).hexdigest()
        entry = {
            "index": len(self.entries) + 1,
            "actor_id": actor_id,
            "action": action,
            "resource": resource,
            "metadata": metadata or {},
            "timestamp": timestamp,
            "prev_hash": self.last_hash,
            "hash": digest
        }
        self.entries.append(entry)
        self.last_hash = digest
        return digest

audit_logger = ImmutableAuditLog()
