"""Distributed Locking and Raft Consensus - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class CoordinationLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class CoordinationStateMachine:
    def __init__(self, initial_state: CoordinationLifecycleState = CoordinationLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[CoordinationLifecycleState, Set[CoordinationLifecycleState]] = {
            CoordinationLifecycleState.INITIAL: {CoordinationLifecycleState.PROVISIONED, CoordinationLifecycleState.FAILED},
            CoordinationLifecycleState.PROVISIONED: {CoordinationLifecycleState.ACTIVE, CoordinationLifecycleState.FAILED},
            CoordinationLifecycleState.ACTIVE: {CoordinationLifecycleState.PAUSED, CoordinationLifecycleState.DRAINING, CoordinationLifecycleState.FAILED},
            CoordinationLifecycleState.PAUSED: {CoordinationLifecycleState.ACTIVE, CoordinationLifecycleState.DRAINING, CoordinationLifecycleState.FAILED},
            CoordinationLifecycleState.DRAINING: {CoordinationLifecycleState.TERMINATED, CoordinationLifecycleState.FAILED},
            CoordinationLifecycleState.TERMINATED: set(),
            CoordinationLifecycleState.FAILED: {CoordinationLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[CoordinationLifecycleState, CoordinationLifecycleState], None]] = []

    def transition_to(self, new_state: CoordinationLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for coordination: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[CoordinationLifecycleState, CoordinationLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == CoordinationLifecycleState.ACTIVE

    def can_transition_to(self, target: CoordinationLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
