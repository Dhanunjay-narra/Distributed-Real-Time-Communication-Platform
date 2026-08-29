"""Safety Scanning and Sanctions Queue - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class ModerationLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class ModerationStateMachine:
    def __init__(self, initial_state: ModerationLifecycleState = ModerationLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[ModerationLifecycleState, Set[ModerationLifecycleState]] = {
            ModerationLifecycleState.INITIAL: {ModerationLifecycleState.PROVISIONED, ModerationLifecycleState.FAILED},
            ModerationLifecycleState.PROVISIONED: {ModerationLifecycleState.ACTIVE, ModerationLifecycleState.FAILED},
            ModerationLifecycleState.ACTIVE: {ModerationLifecycleState.PAUSED, ModerationLifecycleState.DRAINING, ModerationLifecycleState.FAILED},
            ModerationLifecycleState.PAUSED: {ModerationLifecycleState.ACTIVE, ModerationLifecycleState.DRAINING, ModerationLifecycleState.FAILED},
            ModerationLifecycleState.DRAINING: {ModerationLifecycleState.TERMINATED, ModerationLifecycleState.FAILED},
            ModerationLifecycleState.TERMINATED: set(),
            ModerationLifecycleState.FAILED: {ModerationLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[ModerationLifecycleState, ModerationLifecycleState], None]] = []

    def transition_to(self, new_state: ModerationLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for moderation: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[ModerationLifecycleState, ModerationLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == ModerationLifecycleState.ACTIVE

    def can_transition_to(self, target: ModerationLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
