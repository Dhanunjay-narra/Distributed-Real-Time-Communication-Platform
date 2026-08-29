"""Hierarchical RBAC and Announcement Channels - Latency Percentile Calculator (P50, P90, P99).
"""
import time
from typing import List, Dict, Any

class GroupsPercentileCalculator:
    def __init__(self):
        self.samples: List[float] = []

    def add_latency(self, latency_ms: float):
        self.samples.append(latency_ms)
        if len(self.samples) > 5000:
            self.samples.pop(0)

    def calculate_percentiles(self) -> Dict[str, float]:
        if not self.samples:
            return {"p50": 0.0, "p90": 0.0, "p99": 0.0}
        sorted_s = sorted(self.samples)
        n = len(sorted_s)
        return {
            "p50": sorted_s[int(n * 0.50)],
            "p90": sorted_s[min(n - 1, int(n * 0.90))],
            "p99": sorted_s[min(n - 1, int(n * 0.99))]
        }
