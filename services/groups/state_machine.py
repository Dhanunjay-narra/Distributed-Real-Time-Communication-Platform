"""Hierarchical RBAC and Announcement Channels - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class GroupsLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class GroupsStateMachine:
    def __init__(self, initial_state: GroupsLifecycleState = GroupsLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[GroupsLifecycleState, Set[GroupsLifecycleState]] = {
            GroupsLifecycleState.INITIAL: {GroupsLifecycleState.PROVISIONED, GroupsLifecycleState.FAILED},
            GroupsLifecycleState.PROVISIONED: {GroupsLifecycleState.ACTIVE, GroupsLifecycleState.FAILED},
            GroupsLifecycleState.ACTIVE: {GroupsLifecycleState.PAUSED, GroupsLifecycleState.DRAINING, GroupsLifecycleState.FAILED},
            GroupsLifecycleState.PAUSED: {GroupsLifecycleState.ACTIVE, GroupsLifecycleState.DRAINING, GroupsLifecycleState.FAILED},
            GroupsLifecycleState.DRAINING: {GroupsLifecycleState.TERMINATED, GroupsLifecycleState.FAILED},
            GroupsLifecycleState.TERMINATED: set(),
            GroupsLifecycleState.FAILED: {GroupsLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[GroupsLifecycleState, GroupsLifecycleState], None]] = []

    def transition_to(self, new_state: GroupsLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for groups: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[GroupsLifecycleState, GroupsLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == GroupsLifecycleState.ACTIVE

    def can_transition_to(self, target: GroupsLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
