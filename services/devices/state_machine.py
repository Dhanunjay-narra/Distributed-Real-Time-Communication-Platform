"""Hardware Trust and Device Registry - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class DevicesLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class DevicesStateMachine:
    def __init__(self, initial_state: DevicesLifecycleState = DevicesLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[DevicesLifecycleState, Set[DevicesLifecycleState]] = {
            DevicesLifecycleState.INITIAL: {DevicesLifecycleState.PROVISIONED, DevicesLifecycleState.FAILED},
            DevicesLifecycleState.PROVISIONED: {DevicesLifecycleState.ACTIVE, DevicesLifecycleState.FAILED},
            DevicesLifecycleState.ACTIVE: {DevicesLifecycleState.PAUSED, DevicesLifecycleState.DRAINING, DevicesLifecycleState.FAILED},
            DevicesLifecycleState.PAUSED: {DevicesLifecycleState.ACTIVE, DevicesLifecycleState.DRAINING, DevicesLifecycleState.FAILED},
            DevicesLifecycleState.DRAINING: {DevicesLifecycleState.TERMINATED, DevicesLifecycleState.FAILED},
            DevicesLifecycleState.TERMINATED: set(),
            DevicesLifecycleState.FAILED: {DevicesLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[DevicesLifecycleState, DevicesLifecycleState], None]] = []

    def transition_to(self, new_state: DevicesLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for devices: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[DevicesLifecycleState, DevicesLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == DevicesLifecycleState.ACTIVE

    def can_transition_to(self, target: DevicesLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
