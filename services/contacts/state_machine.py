"""Social Contact Graph and Discovery - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class ContactsLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class ContactsStateMachine:
    def __init__(self, initial_state: ContactsLifecycleState = ContactsLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[ContactsLifecycleState, Set[ContactsLifecycleState]] = {
            ContactsLifecycleState.INITIAL: {ContactsLifecycleState.PROVISIONED, ContactsLifecycleState.FAILED},
            ContactsLifecycleState.PROVISIONED: {ContactsLifecycleState.ACTIVE, ContactsLifecycleState.FAILED},
            ContactsLifecycleState.ACTIVE: {ContactsLifecycleState.PAUSED, ContactsLifecycleState.DRAINING, ContactsLifecycleState.FAILED},
            ContactsLifecycleState.PAUSED: {ContactsLifecycleState.ACTIVE, ContactsLifecycleState.DRAINING, ContactsLifecycleState.FAILED},
            ContactsLifecycleState.DRAINING: {ContactsLifecycleState.TERMINATED, ContactsLifecycleState.FAILED},
            ContactsLifecycleState.TERMINATED: set(),
            ContactsLifecycleState.FAILED: {ContactsLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[ContactsLifecycleState, ContactsLifecycleState], None]] = []

    def transition_to(self, new_state: ContactsLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for contacts: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[ContactsLifecycleState, ContactsLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == ContactsLifecycleState.ACTIVE

    def can_transition_to(self, target: ContactsLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
