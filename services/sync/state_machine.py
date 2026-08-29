"""Vector Clock Replication and Offline Recovery - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class SyncLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class SyncStateMachine:
    def __init__(self, initial_state: SyncLifecycleState = SyncLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[SyncLifecycleState, Set[SyncLifecycleState]] = {
            SyncLifecycleState.INITIAL: {SyncLifecycleState.PROVISIONED, SyncLifecycleState.FAILED},
            SyncLifecycleState.PROVISIONED: {SyncLifecycleState.ACTIVE, SyncLifecycleState.FAILED},
            SyncLifecycleState.ACTIVE: {SyncLifecycleState.PAUSED, SyncLifecycleState.DRAINING, SyncLifecycleState.FAILED},
            SyncLifecycleState.PAUSED: {SyncLifecycleState.ACTIVE, SyncLifecycleState.DRAINING, SyncLifecycleState.FAILED},
            SyncLifecycleState.DRAINING: {SyncLifecycleState.TERMINATED, SyncLifecycleState.FAILED},
            SyncLifecycleState.TERMINATED: set(),
            SyncLifecycleState.FAILED: {SyncLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[SyncLifecycleState, SyncLifecycleState], None]] = []

    def transition_to(self, new_state: SyncLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for sync: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[SyncLifecycleState, SyncLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == SyncLifecycleState.ACTIVE

    def can_transition_to(self, target: SyncLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
