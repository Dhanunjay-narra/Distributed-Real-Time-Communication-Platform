import asyncio, json
from typing import Dict, List, Any, Callable, Optional
from packages.common.logger import get_logger
from packages.events.schemas import DomainEvent, MessageSentEvent, GroupCreatedEvent
from packages.events.bus import get_event_bus

logger = get_logger("event-consumers")

class DeadLetterQueue:
    def __init__(self):
        self._dlq_records: List[Dict[str, Any]] = []

    def push(self, topic: str, event: DomainEvent, error: str):
        record = {
            "topic": topic,
            "event_id": event.event_id,
            "event_type": event.event_type,
            "partition_key": event.partition_key,
            "payload": event.to_payload(),
            "error": error,
            "timestamp": event.timestamp.isoformat()
        }
        self._dlq_records.append(record)
        logger.error(f"[DLQ] Event routed to Dead-Letter Queue: {event.event_type} on {topic} -> {error}")

    def list_records(self) -> List[Dict[str, Any]]:
        return list(self._dlq_records)

dlq = DeadLetterQueue()

class ConsumerGroup:
    def __init__(self, group_name: str, max_retries: int = 3):
        self.group_name = group_name
        self.max_retries = max_retries
        self._handlers: Dict[str, List[Callable]] = {}

    def register(self, event_type: str, handler: Callable):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def process_event(self, topic: str, event: DomainEvent):
        handlers = self._handlers.get(event.event_type, [])
        if not handlers:
            return

        for handler in handlers:
            attempt = 0
            while attempt < self.max_retries:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                    break
                except Exception as e:
                    attempt += 1
                    logger.warning(f"Consumer [{self.group_name}] attempt {attempt}/{self.max_retries} failed for event {event.event_id}: {e}")
                    if attempt >= self.max_retries:
                        dlq.push(topic=topic, event=event, error=str(e))
