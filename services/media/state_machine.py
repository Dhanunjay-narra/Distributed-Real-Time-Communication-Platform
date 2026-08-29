"""Multipart Chunking and Transcoding Pipeline - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class MediaLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class MediaStateMachine:
    def __init__(self, initial_state: MediaLifecycleState = MediaLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[MediaLifecycleState, Set[MediaLifecycleState]] = {
            MediaLifecycleState.INITIAL: {MediaLifecycleState.PROVISIONED, MediaLifecycleState.FAILED},
            MediaLifecycleState.PROVISIONED: {MediaLifecycleState.ACTIVE, MediaLifecycleState.FAILED},
            MediaLifecycleState.ACTIVE: {MediaLifecycleState.PAUSED, MediaLifecycleState.DRAINING, MediaLifecycleState.FAILED},
            MediaLifecycleState.PAUSED: {MediaLifecycleState.ACTIVE, MediaLifecycleState.DRAINING, MediaLifecycleState.FAILED},
            MediaLifecycleState.DRAINING: {MediaLifecycleState.TERMINATED, MediaLifecycleState.FAILED},
            MediaLifecycleState.TERMINATED: set(),
            MediaLifecycleState.FAILED: {MediaLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[MediaLifecycleState, MediaLifecycleState], None]] = []

    def transition_to(self, new_state: MediaLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for media: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[MediaLifecycleState, MediaLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == MediaLifecycleState.ACTIVE

    def can_transition_to(self, target: MediaLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
