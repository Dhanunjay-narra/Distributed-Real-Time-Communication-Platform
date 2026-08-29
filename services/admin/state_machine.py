"""Operations Control Center and Telemetry - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class AdminLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class AdminStateMachine:
    def __init__(self, initial_state: AdminLifecycleState = AdminLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[AdminLifecycleState, Set[AdminLifecycleState]] = {
            AdminLifecycleState.INITIAL: {AdminLifecycleState.PROVISIONED, AdminLifecycleState.FAILED},
            AdminLifecycleState.PROVISIONED: {AdminLifecycleState.ACTIVE, AdminLifecycleState.FAILED},
            AdminLifecycleState.ACTIVE: {AdminLifecycleState.PAUSED, AdminLifecycleState.DRAINING, AdminLifecycleState.FAILED},
            AdminLifecycleState.PAUSED: {AdminLifecycleState.ACTIVE, AdminLifecycleState.DRAINING, AdminLifecycleState.FAILED},
            AdminLifecycleState.DRAINING: {AdminLifecycleState.TERMINATED, AdminLifecycleState.FAILED},
            AdminLifecycleState.TERMINATED: set(),
            AdminLifecycleState.FAILED: {AdminLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[AdminLifecycleState, AdminLifecycleState], None]] = []

    def transition_to(self, new_state: AdminLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for admin: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[AdminLifecycleState, AdminLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == AdminLifecycleState.ACTIVE

    def can_transition_to(self, target: AdminLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
