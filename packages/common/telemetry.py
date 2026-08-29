import time
from typing import Dict, Any

class TelemetryCollector:
    def __init__(self):
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}

    def increment(self, metric_name: str, value: int = 1):
        self.counters[metric_name] = self.counters.get(metric_name, 0) + value

    def set_gauge(self, metric_name: str, value: float):
        self.gauges[metric_name] = value

    def snapshot(self) -> Dict[str, Any]:
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "timestamp": time.time()
        }

telemetry = TelemetryCollector()
