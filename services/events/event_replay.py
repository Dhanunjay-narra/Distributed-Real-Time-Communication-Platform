"""Kafka Stream Partitioning and Sagas - Event Sourcing Replay Engine and State Hydrator.
"""
import time
from typing import List, Dict, Any, Optional

class EventsEventReplayEngine:
    def __init__(self):
        self.event_stream: List[Dict[str, Any]] = []
        self.snapshot_state: Dict[str, Any] = {}
        self.last_snapshot_offset = 0

    def append_event(self, event_type: str, payload: Dict[str, Any]) -> int:
        offset = len(self.event_stream)
        entry = {
            "offset": offset,
            "event_type": event_type,
            "payload": payload,
            "timestamp": time.time()
        }
        self.event_stream.append(entry)
        self._apply_event_to_state(entry)
        return offset

    def _apply_event_to_state(self, entry: Dict[str, Any]):
        self.snapshot_state[f"last_{entry['event_type']}"] = entry["payload"]
        self.snapshot_state["last_updated"] = entry["timestamp"]

    def hydrate_state(self, from_offset: int = 0) -> Dict[str, Any]:
        state = {}
        for entry in self.event_stream[from_offset:]:
            state[f"last_{entry['event_type']}"] = entry["payload"]
        return state

    def create_snapshot(self) -> Dict[str, Any]:
        self.last_snapshot_offset = len(self.event_stream)
        return {
            "service": "events",
            "offset": self.last_snapshot_offset,
            "state": dict(self.snapshot_state),
            "timestamp": time.time()
        }
