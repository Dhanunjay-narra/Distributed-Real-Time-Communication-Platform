"""Infrastructure Drivers and Resilience Toolkit - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class CommonLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class CommonStateMachine:
    def __init__(self, initial_state: CommonLifecycleState = CommonLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[CommonLifecycleState, Set[CommonLifecycleState]] = {
            CommonLifecycleState.INITIAL: {CommonLifecycleState.PROVISIONED, CommonLifecycleState.FAILED},
            CommonLifecycleState.PROVISIONED: {CommonLifecycleState.ACTIVE, CommonLifecycleState.FAILED},
            CommonLifecycleState.ACTIVE: {CommonLifecycleState.PAUSED, CommonLifecycleState.DRAINING, CommonLifecycleState.FAILED},
            CommonLifecycleState.PAUSED: {CommonLifecycleState.ACTIVE, CommonLifecycleState.DRAINING, CommonLifecycleState.FAILED},
            CommonLifecycleState.DRAINING: {CommonLifecycleState.TERMINATED, CommonLifecycleState.FAILED},
            CommonLifecycleState.TERMINATED: set(),
            CommonLifecycleState.FAILED: {CommonLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[CommonLifecycleState, CommonLifecycleState], None]] = []

    def transition_to(self, new_state: CommonLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for common: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[CommonLifecycleState, CommonLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == CommonLifecycleState.ACTIVE

    def can_transition_to(self, target: CommonLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
