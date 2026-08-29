"""Reverse Proxy and Correlation Ingress - Finite State Machine and Lifecycle Coordinator.
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Any
from packages.common.exceptions import ConflictException

class ApiGatewayLifecycleState(str, Enum):
    INITIAL = "INITIAL"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"

class ApiGatewayStateMachine:
    def __init__(self, initial_state: ApiGatewayLifecycleState = ApiGatewayLifecycleState.INITIAL):
        self.current_state = initial_state
        self._transitions: Dict[ApiGatewayLifecycleState, Set[ApiGatewayLifecycleState]] = {
            ApiGatewayLifecycleState.INITIAL: {ApiGatewayLifecycleState.PROVISIONED, ApiGatewayLifecycleState.FAILED},
            ApiGatewayLifecycleState.PROVISIONED: {ApiGatewayLifecycleState.ACTIVE, ApiGatewayLifecycleState.FAILED},
            ApiGatewayLifecycleState.ACTIVE: {ApiGatewayLifecycleState.PAUSED, ApiGatewayLifecycleState.DRAINING, ApiGatewayLifecycleState.FAILED},
            ApiGatewayLifecycleState.PAUSED: {ApiGatewayLifecycleState.ACTIVE, ApiGatewayLifecycleState.DRAINING, ApiGatewayLifecycleState.FAILED},
            ApiGatewayLifecycleState.DRAINING: {ApiGatewayLifecycleState.TERMINATED, ApiGatewayLifecycleState.FAILED},
            ApiGatewayLifecycleState.TERMINATED: set(),
            ApiGatewayLifecycleState.FAILED: {ApiGatewayLifecycleState.INITIAL}
        }
        self._listeners: List[Callable[[ApiGatewayLifecycleState, ApiGatewayLifecycleState], None]] = []

    def transition_to(self, new_state: ApiGatewayLifecycleState) -> bool:
        allowed = self._transitions.get(self.current_state, set())
        if new_state not in allowed:
            raise ConflictException(f"Invalid state transition for api_gateway: {self.current_state} -> {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass
        return True

    def register_transition_hook(self, hook: Callable[[ApiGatewayLifecycleState, ApiGatewayLifecycleState], None]):
        self._listeners.append(hook)

    def is_active(self) -> bool:
        return self.current_state == ApiGatewayLifecycleState.ACTIVE

    def can_transition_to(self, target: ApiGatewayLifecycleState) -> bool:
        return target in self._transitions.get(self.current_state, set())
