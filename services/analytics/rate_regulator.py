"""Time-Series Aggregations and DAU Metrics - Leaky Bucket Rate Regulator and Traffic Shaper.
"""
import time
from typing import Dict, Optional

class AnalyticsRateRegulator:
    def __init__(self, leak_rate_per_sec: float = 50.0, bucket_capacity: float = 200.0):
        self.leak_rate = leak_rate_per_sec
        self.capacity = bucket_capacity
        self.water_level = 0.0
        self.last_leak_time = time.time()

    def request_permit(self, amount: float = 1.0) -> bool:
        now = time.time()
        elapsed = now - self.last_leak_time
        self.water_level = max(0.0, self.water_level - elapsed * self.leak_rate)
        self.last_leak_time = now

        if self.water_level + amount <= self.capacity:
            self.water_level += amount
            return True
        return False

    def get_fill_percentage(self) -> float:
        return (self.water_level / self.capacity) * 100.0
