"""Kafka Stream Partitioning and Sagas - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class EventsLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class EventsStateMachine:
    def __init__(self, initial_state: EventsLifecycleState = EventsLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[EventsLifecycleState, Set[EventsLifecycleState]] = {
            EventsLifecycleState.INITIAL: {EventsLifecycleState.PROVISIONED, EventsLifecycleState.FAILED},
            EventsLifecycleState.PROVISIONED: {EventsLifecycleState.ACTIVE, EventsLifecycleState.FAILED},
            EventsLifecycleState.ACTIVE: {EventsLifecycleState.PAUSED, EventsLifecycleState.DRAINING, EventsLifecycleState.FAILED},
            EventsLifecycleState.PAUSED: {EventsLifecycleState.ACTIVE, EventsLifecycleState.DRAINING, EventsLifecycleState.FAILED},
            EventsLifecycleState.DRAINING: {EventsLifecycleState.TERMINATED, EventsLifecycleState.FAILED},
            EventsLifecycleState.TERMINATED: set(),
            EventsLifecycleState.FAILED: {EventsLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[EventsLifecycleState, EventsLifecycleState], None]] = []

    def transition_to(self, new_state: EventsLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for events: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[EventsLifecycleState, EventsLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == EventsLifecycleState.ACTIVE

    def can_transition_to(self, target: EventsLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
