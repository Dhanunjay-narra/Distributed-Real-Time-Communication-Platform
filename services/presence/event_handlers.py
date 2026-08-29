"""Ephemeral Mesh and Activity Streams - Event Listeners and Stream Processors.
"""
import time, asyncio
from typing import Dict, List, Any, Optional
from packages.common.logger import get_logger
from packages.events.schemas import DomainEvent

logger = get_logger("presence-events")

class PresenceEventHandler:
    def __init__(self):
        self.logger = logger
        self.processed_events: List[str] = []
        self._handlers: Dict[str, List[Any]] = {}

    def subscribe(self, event_type: str, callback: Any):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(callback)

    async def handle_event(self, event: DomainEvent) -> bool:
        self.logger.info(f"Handling event in presence: {event.event_type} (ID: {event.event_id})")
        self.processed_events.append(event.event_id)
        
        callbacks = self._handlers.get(event.event_type, [])
        for cb in callbacks:
            if asyncio.iscoroutinefunction(cb):
                await cb(event)
            else:
                cb(event)
        return True

    def get_event_audit(self) -> Dict[str, Any]:
        return {
            "service": "presence",
            "total_handled": len(self.processed_events),
            "registered_event_types": list(self._handlers.keys())
        }
