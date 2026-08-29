"""Full-Text OpenSearch and Trigram Engine - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class SearchLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class SearchStateMachine:
    def __init__(self, initial_state: SearchLifecycleState = SearchLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[SearchLifecycleState, Set[SearchLifecycleState]] = {
            SearchLifecycleState.INITIAL: {SearchLifecycleState.PROVISIONED, SearchLifecycleState.FAILED},
            SearchLifecycleState.PROVISIONED: {SearchLifecycleState.ACTIVE, SearchLifecycleState.FAILED},
            SearchLifecycleState.ACTIVE: {SearchLifecycleState.PAUSED, SearchLifecycleState.DRAINING, SearchLifecycleState.FAILED},
            SearchLifecycleState.PAUSED: {SearchLifecycleState.ACTIVE, SearchLifecycleState.DRAINING, SearchLifecycleState.FAILED},
            SearchLifecycleState.DRAINING: {SearchLifecycleState.TERMINATED, SearchLifecycleState.FAILED},
            SearchLifecycleState.TERMINATED: set(),
            SearchLifecycleState.FAILED: {SearchLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[SearchLifecycleState, SearchLifecycleState], None]] = []

    def transition_to(self, new_state: SearchLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for search: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[SearchLifecycleState, SearchLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == SearchLifecycleState.ACTIVE

    def can_transition_to(self, target: SearchLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
