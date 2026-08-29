"""WebRTC Voice/Video Signaling Mesh - Real-Time Anomaly Detector and Outlier Scorer.
"""
import math, time
from typing import List, Dict, Any

class CallsAnomalyDetector:
    def __init__(self, window_size: int = 100, std_dev_threshold: float = 3.0):
        self.window_size = window_size
        self.std_dev_threshold = std_dev_threshold
        self.latency_samples: List[float] = []

    def record_sample(self, latency_ms: float) -> bool:
        self.latency_samples.append(latency_ms)
        if len(self.latency_samples) > self.window_size:
            self.latency_samples.pop(0)

        if len(self.latency_samples) < 10:
            return False

        mean = sum(self.latency_samples) / len(self.latency_samples)
        variance = sum((x - mean) ** 2 for x in self.latency_samples) / len(self.latency_samples)
        std_dev = math.sqrt(variance)

        if std_dev > 0 and (latency_ms - mean) / std_dev > self.std_dev_threshold:
            return True
        return False
