"""Distributed Gateway Connection Cluster - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class WebsocketLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class WebsocketStateMachine:
    def __init__(self, initial_state: WebsocketLifecycleState = WebsocketLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[WebsocketLifecycleState, Set[WebsocketLifecycleState]] = {
            WebsocketLifecycleState.INITIAL: {WebsocketLifecycleState.PROVISIONED, WebsocketLifecycleState.FAILED},
            WebsocketLifecycleState.PROVISIONED: {WebsocketLifecycleState.ACTIVE, WebsocketLifecycleState.FAILED},
            WebsocketLifecycleState.ACTIVE: {WebsocketLifecycleState.PAUSED, WebsocketLifecycleState.DRAINING, WebsocketLifecycleState.FAILED},
            WebsocketLifecycleState.PAUSED: {WebsocketLifecycleState.ACTIVE, WebsocketLifecycleState.DRAINING, WebsocketLifecycleState.FAILED},
            WebsocketLifecycleState.DRAINING: {WebsocketLifecycleState.TERMINATED, WebsocketLifecycleState.FAILED},
            WebsocketLifecycleState.TERMINATED: set(),
            WebsocketLifecycleState.FAILED: {WebsocketLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[WebsocketLifecycleState, WebsocketLifecycleState], None]] = []

    def transition_to(self, new_state: WebsocketLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for websocket: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[WebsocketLifecycleState, WebsocketLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == WebsocketLifecycleState.ACTIVE

    def can_transition_to(self, target: WebsocketLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
