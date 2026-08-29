"""Reverse Proxy and Correlation Ingress - Exponential Backoff and Jitter Executor.
"""
import asyncio, random, time
from typing import Callable, Any

class ApiGatewayBackoffExecutor:
    def __init__(self, max_attempts: int = 5, base_delay: float = 0.05, max_delay: float = 2.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay

    async def execute_with_retry(self, operation: Callable, *args, **kwargs) -> Any:
        attempt = 0
        while attempt < self.max_attempts:
            try:
                if asyncio.iscoroutinefunction(operation):
                    return await operation(*args, **kwargs)
                return operation(*args, **kwargs)
            except Exception as e:
                attempt += 1
                if attempt >= self.max_attempts:
                    raise
                delay = min(self.max_delay, self.base_delay * (2 ** (attempt - 1)))
                jitter = random.uniform(0, delay * 0.2)
                await asyncio.sleep(delay + jitter)
