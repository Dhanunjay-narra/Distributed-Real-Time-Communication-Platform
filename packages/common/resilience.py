import asyncio, time, random, functools
from enum import Enum
from typing import Callable, Any, Optional
from .exceptions import ServiceUnavailableException

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(self, name: str, failure_threshold: int = 5, recovery_timeout: float = 30.0, half_open_max_calls: int = 3):
        self.name, self.failure_threshold, self.recovery_timeout, self.half_open_max_calls = name, failure_threshold, recovery_timeout, half_open_max_calls
        self.state, self.failure_count, self.success_count, self.last_state_change = CircuitState.CLOSED, 0, 0, time.time()

    def _update_state(self, new_state: CircuitState):
        self.state = new_state
        self.last_state_change = time.time()
        if new_state == CircuitState.HALF_OPEN: self.success_count = 0

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        now = time.time()
        if self.state == CircuitState.OPEN:
            if now - self.last_state_change > self.recovery_timeout:
                self._update_state(CircuitState.HALF_OPEN)
            else:
                raise ServiceUnavailableException(f"Circuit [{self.name}] is OPEN.")
        try:
            res = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.half_open_max_calls:
                    self.failure_count = 0
                    self._update_state(CircuitState.CLOSED)
            elif self.state == CircuitState.CLOSED: self.failure_count = 0
            return res
        except Exception as e:
            self.failure_count += 1
            if self.state == CircuitState.HALF_OPEN or self.failure_count >= self.failure_threshold:
                self._update_state(CircuitState.OPEN)
            raise e

def retry_with_backoff(max_retries: int = 3, initial_delay: float = 0.2, max_delay: float = 2.0, backoff_factor: float = 2.0):
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(1, max_retries + 1):
                try:
                    if asyncio.iscoroutinefunction(func): return await func(*args, **kwargs)
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries: raise e
                    await asyncio.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
        return wrapper
    return decorator

class Bulkhead:
    def __init__(self, max_concurrent: int = 100):
        self.semaphore = asyncio.Semaphore(max_concurrent)
    async def __aenter__(self):
        await self.semaphore.acquire()
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.semaphore.release()

class RateLimiter:
    def __init__(self, rate: int = 60, per_seconds: int = 60):
        self.rate, self.per_seconds, self.allowance, self.last_check = rate, per_seconds, float(rate), time.time()
        self._lock = asyncio.Lock()
    async def acquire(self) -> bool:
        async with self._lock:
            now = time.time()
            self.allowance = min(float(self.rate), self.allowance + (now - self.last_check) * (self.rate / self.per_seconds))
            self.last_check = now
            if self.allowance < 1.0: return False
            self.allowance -= 1.0
            return True
