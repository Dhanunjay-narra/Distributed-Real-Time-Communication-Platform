"""Time-Series Aggregations and DAU Metrics - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class AnalyticsLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class AnalyticsStateMachine:
    def __init__(self, initial_state: AnalyticsLifecycleState = AnalyticsLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[AnalyticsLifecycleState, Set[AnalyticsLifecycleState]] = {
            AnalyticsLifecycleState.INITIAL: {AnalyticsLifecycleState.PROVISIONED, AnalyticsLifecycleState.FAILED},
            AnalyticsLifecycleState.PROVISIONED: {AnalyticsLifecycleState.ACTIVE, AnalyticsLifecycleState.FAILED},
            AnalyticsLifecycleState.ACTIVE: {AnalyticsLifecycleState.PAUSED, AnalyticsLifecycleState.DRAINING, AnalyticsLifecycleState.FAILED},
            AnalyticsLifecycleState.PAUSED: {AnalyticsLifecycleState.ACTIVE, AnalyticsLifecycleState.DRAINING, AnalyticsLifecycleState.FAILED},
            AnalyticsLifecycleState.DRAINING: {AnalyticsLifecycleState.TERMINATED, AnalyticsLifecycleState.FAILED},
            AnalyticsLifecycleState.TERMINATED: set(),
            AnalyticsLifecycleState.FAILED: {AnalyticsLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[AnalyticsLifecycleState, AnalyticsLifecycleState], None]] = []

    def transition_to(self, new_state: AnalyticsLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for analytics: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[AnalyticsLifecycleState, AnalyticsLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == AnalyticsLifecycleState.ACTIVE

    def can_transition_to(self, target: AnalyticsLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
