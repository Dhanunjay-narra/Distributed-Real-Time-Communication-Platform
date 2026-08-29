"""Ephemeral Mesh and Activity Streams - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class PresenceLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class PresenceStateMachine:
    def __init__(self, initial_state: PresenceLifecycleState = PresenceLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[PresenceLifecycleState, Set[PresenceLifecycleState]] = {
            PresenceLifecycleState.INITIAL: {PresenceLifecycleState.PROVISIONED, PresenceLifecycleState.FAILED},
            PresenceLifecycleState.PROVISIONED: {PresenceLifecycleState.ACTIVE, PresenceLifecycleState.FAILED},
            PresenceLifecycleState.ACTIVE: {PresenceLifecycleState.PAUSED, PresenceLifecycleState.DRAINING, PresenceLifecycleState.FAILED},
            PresenceLifecycleState.PAUSED: {PresenceLifecycleState.ACTIVE, PresenceLifecycleState.DRAINING, PresenceLifecycleState.FAILED},
            PresenceLifecycleState.DRAINING: {PresenceLifecycleState.TERMINATED, PresenceLifecycleState.FAILED},
            PresenceLifecycleState.TERMINATED: set(),
            PresenceLifecycleState.FAILED: {PresenceLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[PresenceLifecycleState, PresenceLifecycleState], None]] = []

    def transition_to(self, new_state: PresenceLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for presence: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[PresenceLifecycleState, PresenceLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == PresenceLifecycleState.ACTIVE

    def can_transition_to(self, target: PresenceLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
