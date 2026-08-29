"""Hierarchical RBAC and Announcement Channels - Bulkhead Isolation and Thread Pool Concurrency Limiter.
Platform: Chatbot Distributed Real-Time Communication Platform.
"""
import asyncio, time
from typing import Callable, Any, Optional

class GroupsBulkheadIsolator:
    def __init__(self, max_concurrent: int = 50, max_queue: int = 100):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.max_queue = max_queue
        self.queued_count = 0

    async def execute(self, coro_fn: Callable, *args, **kwargs) -> Any:
        if self.queued_count >= self.max_queue:
            raise BufferError(f"Bulkhead queue full for groups")
        
        self.queued_count += 1
        try:
            async with self.semaphore:
                self.queued_count -= 1
                if asyncio.iscoroutinefunction(coro_fn):
                    return await coro_fn(*args, **kwargs)
                return coro_fn(*args, **kwargs)
        except Exception:
            self.queued_count = max(0, self.queued_count - 1)
            raise
