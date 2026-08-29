import asyncio, json
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Any
from .schemas import DomainEvent
from packages.common.logger import get_logger

logger = get_logger("event-bus")

class EventBus(ABC):
    @abstractmethod
    async def publish(self, topic: str, event: DomainEvent) -> None: pass
    @abstractmethod
    async def subscribe(self, topic: str, handler: Callable[[DomainEvent], Any]) -> None: pass

class InMemoryEventBus(EventBus):
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._dlq: List[Dict[str, Any]] = []

    async def publish(self, topic: str, event: DomainEvent) -> None:
        for handler in self._subscribers.get(topic, []):
            try:
                if asyncio.iscoroutinefunction(handler): asyncio.create_task(handler(event))
                else: handler(event)
            except Exception as e:
                self._dlq.append({"topic": topic, "event": event.to_payload(), "error": str(e)})

    async def subscribe(self, topic: str, handler: Callable[[DomainEvent], Any]) -> None:
        if topic not in self._subscribers: self._subscribers[topic] = []
        self._subscribers[topic].append(handler)

_bus = InMemoryEventBus()
def get_event_bus() -> EventBus: return _bus
