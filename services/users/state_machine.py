"""User Profiles and Presence Status - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class UsersLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class UsersStateMachine:
    def __init__(self, initial_state: UsersLifecycleState = UsersLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[UsersLifecycleState, Set[UsersLifecycleState]] = {
            UsersLifecycleState.INITIAL: {UsersLifecycleState.PROVISIONED, UsersLifecycleState.FAILED},
            UsersLifecycleState.PROVISIONED: {UsersLifecycleState.ACTIVE, UsersLifecycleState.FAILED},
            UsersLifecycleState.ACTIVE: {UsersLifecycleState.PAUSED, UsersLifecycleState.DRAINING, UsersLifecycleState.FAILED},
            UsersLifecycleState.PAUSED: {UsersLifecycleState.ACTIVE, UsersLifecycleState.DRAINING, UsersLifecycleState.FAILED},
            UsersLifecycleState.DRAINING: {UsersLifecycleState.TERMINATED, UsersLifecycleState.FAILED},
            UsersLifecycleState.TERMINATED: set(),
            UsersLifecycleState.FAILED: {UsersLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[UsersLifecycleState, UsersLifecycleState], None]] = []

    def transition_to(self, new_state: UsersLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for users: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[UsersLifecycleState, UsersLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == UsersLifecycleState.ACTIVE

    def can_transition_to(self, target: UsersLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
