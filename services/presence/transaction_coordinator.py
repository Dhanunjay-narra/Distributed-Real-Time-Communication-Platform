"""Ephemeral Mesh and Activity Streams - Transaction Coordinator and Concurrency Manager.
"""
import asyncio, time, uuid
from typing import Dict, List, Any, Optional

class PresenceTransactionCoordinator:
    def __init__(self):
        self.active_transactions: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def begin_transaction(self, initiator_id: str, context: Dict[str, Any]) -> str:
        tx_id = f"tx_presence_{uuid.uuid4()}"
        async with self._lock:
            self.active_transactions[tx_id] = {
                "tx_id": tx_id,
                "initiator_id": initiator_id,
                "start_time": time.time(),
                "status": "PREPARED",
                "context": context
            }
        return tx_id

    async def commit_transaction(self, tx_id: str) -> bool:
        async with self._lock:
            if tx_id in self.active_transactions:
                self.active_transactions[tx_id]["status"] = "COMMITTED"
                self.active_transactions[tx_id]["commit_time"] = time.time()
                return True
        return False

    async def rollback_transaction(self, tx_id: str, reason: str) -> bool:
        async with self._lock:
            if tx_id in self.active_transactions:
                self.active_transactions[tx_id]["status"] = "ABORTED"
                self.active_transactions[tx_id]["abort_reason"] = reason
                return True
        return False

    def list_active_transactions(self) -> List[Dict[str, Any]]:
        return list(self.active_transactions.values())
