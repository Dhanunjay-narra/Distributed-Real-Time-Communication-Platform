"""Granular Privacy Matrix and Disappearing Messages - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class PrivacyLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class PrivacyStateMachine:
    def __init__(self, initial_state: PrivacyLifecycleState = PrivacyLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[PrivacyLifecycleState, Set[PrivacyLifecycleState]] = {
            PrivacyLifecycleState.INITIAL: {PrivacyLifecycleState.PROVISIONED, PrivacyLifecycleState.FAILED},
            PrivacyLifecycleState.PROVISIONED: {PrivacyLifecycleState.ACTIVE, PrivacyLifecycleState.FAILED},
            PrivacyLifecycleState.ACTIVE: {PrivacyLifecycleState.PAUSED, PrivacyLifecycleState.DRAINING, PrivacyLifecycleState.FAILED},
            PrivacyLifecycleState.PAUSED: {PrivacyLifecycleState.ACTIVE, PrivacyLifecycleState.DRAINING, PrivacyLifecycleState.FAILED},
            PrivacyLifecycleState.DRAINING: {PrivacyLifecycleState.TERMINATED, PrivacyLifecycleState.FAILED},
            PrivacyLifecycleState.TERMINATED: set(),
            PrivacyLifecycleState.FAILED: {PrivacyLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[PrivacyLifecycleState, PrivacyLifecycleState], None]] = []

    def transition_to(self, new_state: PrivacyLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for privacy: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[PrivacyLifecycleState, PrivacyLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == PrivacyLifecycleState.ACTIVE

    def can_transition_to(self, target: PrivacyLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
