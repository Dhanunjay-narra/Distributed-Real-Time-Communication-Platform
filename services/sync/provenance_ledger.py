"""Vector Clock Replication and Offline Recovery - Cryptographic Provenance Ledger.
"""
import hashlib, time
from typing import Dict, List, Any, Optional

class SyncProvenanceEntry:
    def __init__(self, index: int, previous_hash: str, actor_id: str, change_type: str, data_snapshot: Dict[str, Any]):
        self.index = index
        self.timestamp = time.time()
        self.previous_hash = previous_hash
        self.actor_id = actor_id
        self.change_type = change_type
        self.data_snapshot = data_snapshot
        self.hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        raw = f"{self.index}|{self.timestamp}|{self.previous_hash}|{self.actor_id}|{self.change_type}|{self.data_snapshot}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

class SyncProvenanceLedger:
    def __init__(self):
        self.chain: List[SyncProvenanceEntry] = []
        self._genesis_hash = "0" * 64

    def record_change(self, actor_id: str, change_type: str, data_snapshot: Dict[str, Any]) -> str:
        prev_hash = self.chain[-1].hash if self.chain else self._genesis_hash
        entry = SyncProvenanceEntry(
            index=len(self.chain) + 1,
            previous_hash=prev_hash,
            actor_id=actor_id,
            change_type=change_type,
            data_snapshot=data_snapshot
        )
        self.chain.append(entry)
        return entry.hash

    def verify_integrity(self) -> bool:
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]
            if curr.previous_hash != prev.hash:
                return False
            if curr.hash != curr._calculate_hash():
                return False
        return True
