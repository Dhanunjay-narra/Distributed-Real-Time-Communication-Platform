"""Reverse Proxy and Correlation Ingress - Adaptive Load Shedder and Priority Drop Arbiter.
"""
import time
from typing import Dict, Any

class ApiGatewayAdaptiveLoadShedder:
    def __init__(self, target_latency_ms: float = 50.0):
        self.target_latency_ms = target_latency_ms
        self.current_cpu_load = 0.0
        self.shed_count = 0

    def should_shed_request(self, priority: str = "NORMAL", current_latency_ms: float = 0.0) -> bool:
        if priority == "CRITICAL":
            return False
        if current_latency_ms > self.target_latency_ms * 2:
            self.shed_count += 1
            return True
        return False
