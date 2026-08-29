"""WebRTC Voice/Video Signaling Mesh - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class CallsLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class CallsStateMachine:
    def __init__(self, initial_state: CallsLifecycleState = CallsLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[CallsLifecycleState, Set[CallsLifecycleState]] = {
            CallsLifecycleState.INITIAL: {CallsLifecycleState.PROVISIONED, CallsLifecycleState.FAILED},
            CallsLifecycleState.PROVISIONED: {CallsLifecycleState.ACTIVE, CallsLifecycleState.FAILED},
            CallsLifecycleState.ACTIVE: {CallsLifecycleState.PAUSED, CallsLifecycleState.DRAINING, CallsLifecycleState.FAILED},
            CallsLifecycleState.PAUSED: {CallsLifecycleState.ACTIVE, CallsLifecycleState.DRAINING, CallsLifecycleState.FAILED},
            CallsLifecycleState.DRAINING: {CallsLifecycleState.TERMINATED, CallsLifecycleState.FAILED},
            CallsLifecycleState.TERMINATED: set(),
            CallsLifecycleState.FAILED: {CallsLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[CallsLifecycleState, CallsLifecycleState], None]] = []

    def transition_to(self, new_state: CallsLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for calls: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[CallsLifecycleState, CallsLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == CallsLifecycleState.ACTIVE

    def can_transition_to(self, target: CallsLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
