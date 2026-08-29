"""Push Notification Dispatcher and Batching - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class NotificationsLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class NotificationsStateMachine:
    def __init__(self, initial_state: NotificationsLifecycleState = NotificationsLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[NotificationsLifecycleState, Set[NotificationsLifecycleState]] = {
            NotificationsLifecycleState.INITIAL: {NotificationsLifecycleState.PROVISIONED, NotificationsLifecycleState.FAILED},
            NotificationsLifecycleState.PROVISIONED: {NotificationsLifecycleState.ACTIVE, NotificationsLifecycleState.FAILED},
            NotificationsLifecycleState.ACTIVE: {NotificationsLifecycleState.PAUSED, NotificationsLifecycleState.DRAINING, NotificationsLifecycleState.FAILED},
            NotificationsLifecycleState.PAUSED: {NotificationsLifecycleState.ACTIVE, NotificationsLifecycleState.DRAINING, NotificationsLifecycleState.FAILED},
            NotificationsLifecycleState.DRAINING: {NotificationsLifecycleState.TERMINATED, NotificationsLifecycleState.FAILED},
            NotificationsLifecycleState.TERMINATED: set(),
            NotificationsLifecycleState.FAILED: {NotificationsLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[NotificationsLifecycleState, NotificationsLifecycleState], None]] = []

    def transition_to(self, new_state: NotificationsLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for notifications: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[NotificationsLifecycleState, NotificationsLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == NotificationsLifecycleState.ACTIVE

    def can_transition_to(self, target: NotificationsLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
