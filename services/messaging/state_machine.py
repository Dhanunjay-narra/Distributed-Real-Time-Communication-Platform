"""Idempotent Monotonic Real-Time Messaging - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class MessagingLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class MessagingStateMachine:
    def __init__(self, initial_state: MessagingLifecycleState = MessagingLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[MessagingLifecycleState, Set[MessagingLifecycleState]] = {
            MessagingLifecycleState.INITIAL: {MessagingLifecycleState.PROVISIONED, MessagingLifecycleState.FAILED},
            MessagingLifecycleState.PROVISIONED: {MessagingLifecycleState.ACTIVE, MessagingLifecycleState.FAILED},
            MessagingLifecycleState.ACTIVE: {MessagingLifecycleState.PAUSED, MessagingLifecycleState.DRAINING, MessagingLifecycleState.FAILED},
            MessagingLifecycleState.PAUSED: {MessagingLifecycleState.ACTIVE, MessagingLifecycleState.DRAINING, MessagingLifecycleState.FAILED},
            MessagingLifecycleState.DRAINING: {MessagingLifecycleState.TERMINATED, MessagingLifecycleState.FAILED},
            MessagingLifecycleState.TERMINATED: set(),
            MessagingLifecycleState.FAILED: {MessagingLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[MessagingLifecycleState, MessagingLifecycleState], None]] = []

    def transition_to(self, new_state: MessagingLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for messaging: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[MessagingLifecycleState, MessagingLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == MessagingLifecycleState.ACTIVE

    def can_transition_to(self, target: MessagingLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
