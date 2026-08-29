"""Distributed Gateway Connection Cluster - Metrics Reporter and Prometheus Instrumentation.
"""
import time
from typing import Dict, Any, List

class WebsocketMetricsReporter:
    def __init__(self):
        self.request_counters: Dict[str, int] = {}
        self.error_counters: Dict[str, int] = {}
        self.execution_latencies: List[float] = []

    def record_request(self, endpoint: str):
        self.request_counters[endpoint] = self.request_counters.get(endpoint, 0) + 1

    def record_error(self, endpoint: str, error_type: str):
        key = f"{endpoint}:{error_type}"
        self.error_counters[key] = self.error_counters.get(key, 0) + 1

    def record_latency(self, latency_ms: float):
        self.execution_latencies.append(latency_ms)
        if len(self.execution_latencies) > 2000:
            self.execution_latencies.pop(0)

    def generate_prometheus_payload(self) -> str:
        lines = [
            f"# HELP chatbot_websocket_requests_total Total HTTP requests to websocket",
            f"# TYPE chatbot_websocket_requests_total counter"
        ]
        for ep, count in self.request_counters.items():
            lines.append(f'chatbot_websocket_requests_total{endpoint="{ep}"} {count}')
        return "\n".join(lines)
