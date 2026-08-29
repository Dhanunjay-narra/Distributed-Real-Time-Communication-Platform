"""Reverse Proxy and Correlation Ingress - Network Packet Jitter and RTT Latency Estimator.
"""
import time
from typing import List

class ApiGatewayJitterEstimator:
    def __init__(self):
        self.rtt_history: List[float] = []
        self.estimated_jitter = 0.0

    def record_rtt_sample(self, rtt_ms: float):
        if self.rtt_history:
            prev_rtt = self.rtt_history[-1]
            diff = abs(rtt_ms - prev_rtt)
            self.estimated_jitter += (diff - self.estimated_jitter) / 16.0
        self.rtt_history.append(rtt_ms)
        if len(self.rtt_history) > 1000:
            self.rtt_history.pop(0)
