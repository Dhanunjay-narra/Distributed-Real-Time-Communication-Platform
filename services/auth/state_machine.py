"""Identity and Multi-Factor Device Authentication - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class AuthLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class AuthStateMachine:
    def __init__(self, initial_state: AuthLifecycleState = AuthLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[AuthLifecycleState, Set[AuthLifecycleState]] = {
            AuthLifecycleState.INITIAL: {AuthLifecycleState.PROVISIONED, AuthLifecycleState.FAILED},
            AuthLifecycleState.PROVISIONED: {AuthLifecycleState.ACTIVE, AuthLifecycleState.FAILED},
            AuthLifecycleState.ACTIVE: {AuthLifecycleState.PAUSED, AuthLifecycleState.DRAINING, AuthLifecycleState.FAILED},
            AuthLifecycleState.PAUSED: {AuthLifecycleState.ACTIVE, AuthLifecycleState.DRAINING, AuthLifecycleState.FAILED},
            AuthLifecycleState.DRAINING: {AuthLifecycleState.TERMINATED, AuthLifecycleState.FAILED},
            AuthLifecycleState.TERMINATED: set(),
            AuthLifecycleState.FAILED: {AuthLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[AuthLifecycleState, AuthLifecycleState], None]] = []

    def transition_to(self, new_state: AuthLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for auth: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[AuthLifecycleState, AuthLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == AuthLifecycleState.ACTIVE

    def can_transition_to(self, target: AuthLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
