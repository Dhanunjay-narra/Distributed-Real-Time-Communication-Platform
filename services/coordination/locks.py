import uuid, time, asyncio
from typing import Optional, List
from packages.common.logger import get_logger

logger = get_logger("distributed-lock-manager")

class DistributedLockManager:
    def __init__(self, node_id: str = "node-1"):
        self.node_id = node_id
        self._active_locks = {}
        self._lock = asyncio.Lock()

    async def acquire_lock(self, resource: str, ttl_seconds: float = 10.0) -> Optional[str]:
        lease_id = str(uuid.uuid4())
        now = time.time()
        
        async with self._lock:
            if resource in self._active_locks:
                owner, exp = self._active_locks[resource]
                if exp > now:
                    return None
            
            self._active_locks[resource] = (lease_id, now + ttl_seconds)
            logger.info(f"Lock acquired on [{resource}] by [{self.node_id}] with lease [{lease_id}]")
            return lease_id

    async def release_lock(self, resource: str, lease_id: str) -> bool:
        async with self._lock:
            if resource in self._active_locks:
                owner, exp = self._active_locks[resource]
                if owner == lease_id:
                    del self._active_locks[resource]
                    logger.info(f"Lock released on [{resource}] with lease [{lease_id}]")
                    return True
        return False
