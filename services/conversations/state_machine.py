"""Conversation Partitioning and Channels - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class ConversationsLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class ConversationsStateMachine:
    def __init__(self, initial_state: ConversationsLifecycleState = ConversationsLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[ConversationsLifecycleState, Set[ConversationsLifecycleState]] = {
            ConversationsLifecycleState.INITIAL: {ConversationsLifecycleState.PROVISIONED, ConversationsLifecycleState.FAILED},
            ConversationsLifecycleState.PROVISIONED: {ConversationsLifecycleState.ACTIVE, ConversationsLifecycleState.FAILED},
            ConversationsLifecycleState.ACTIVE: {ConversationsLifecycleState.PAUSED, ConversationsLifecycleState.DRAINING, ConversationsLifecycleState.FAILED},
            ConversationsLifecycleState.PAUSED: {ConversationsLifecycleState.ACTIVE, ConversationsLifecycleState.DRAINING, ConversationsLifecycleState.FAILED},
            ConversationsLifecycleState.DRAINING: {ConversationsLifecycleState.TERMINATED, ConversationsLifecycleState.FAILED},
            ConversationsLifecycleState.TERMINATED: set(),
            ConversationsLifecycleState.FAILED: {ConversationsLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[ConversationsLifecycleState, ConversationsLifecycleState], None]] = []

    def transition_to(self, new_state: ConversationsLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for conversations: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[ConversationsLifecycleState, ConversationsLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == ConversationsLifecycleState.ACTIVE

    def can_transition_to(self, target: ConversationsLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
