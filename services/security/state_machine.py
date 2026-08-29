"""Cryptography and Double Ratchet Engine - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class SecurityLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class SecurityStateMachine:
    def __init__(self, initial_state: SecurityLifecycleState = SecurityLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[SecurityLifecycleState, Set[SecurityLifecycleState]] = {
            SecurityLifecycleState.INITIAL: {SecurityLifecycleState.PROVISIONED, SecurityLifecycleState.FAILED},
            SecurityLifecycleState.PROVISIONED: {SecurityLifecycleState.ACTIVE, SecurityLifecycleState.FAILED},
            SecurityLifecycleState.ACTIVE: {SecurityLifecycleState.PAUSED, SecurityLifecycleState.DRAINING, SecurityLifecycleState.FAILED},
            SecurityLifecycleState.PAUSED: {SecurityLifecycleState.ACTIVE, SecurityLifecycleState.DRAINING, SecurityLifecycleState.FAILED},
            SecurityLifecycleState.DRAINING: {SecurityLifecycleState.TERMINATED, SecurityLifecycleState.FAILED},
            SecurityLifecycleState.TERMINATED: set(),
            SecurityLifecycleState.FAILED: {SecurityLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[SecurityLifecycleState, SecurityLifecycleState], None]] = []

    def transition_to(self, new_state: SecurityLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for security: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[SecurityLifecycleState, SecurityLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == SecurityLifecycleState.ACTIVE

    def can_transition_to(self, target: SecurityLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
