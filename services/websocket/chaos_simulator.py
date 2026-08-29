"""Distributed Gateway Connection Cluster - Fault Injection and Network Partition Simulator.
"""
import random, asyncio
from typing import Optional, Callable, Any

class WebsocketChaosSimulator:
    def __init__(self, latency_jitter_ms: float = 0.0, drop_rate: float = 0.0):
        self.latency_jitter_ms = latency_jitter_ms
        self.drop_rate = drop_rate
        self.is_enabled = False

    def configure(self, latency_jitter_ms: float, drop_rate: float):
        self.latency_jitter_ms = latency_jitter_ms
        self.drop_rate = drop_rate
        self.is_enabled = drop_rate > 0 or latency_jitter_ms > 0

    async def execute_with_chaos(self, fn: Callable, *args, **kwargs) -> Any:
        if not self.is_enabled:
            if asyncio.iscoroutinefunction(fn):
                return await fn(*args, **kwargs)
            return fn(*args, **kwargs)

        if random.random() < self.drop_rate:
            raise ConnectionResetError(f"Chaos injected simulated network drop for websocket")

        if self.latency_jitter_ms > 0:
            delay = random.uniform(0, self.latency_jitter_ms / 1000.0)
            await asyncio.sleep(delay)

        if asyncio.iscoroutinefunction(fn):
            return await fn(*args, **kwargs)
        return fn(*args, **kwargs)
