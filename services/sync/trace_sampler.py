"""Vector Clock Replication and Offline Recovery - Adaptive Distributed Trace Sampler.
"""
import random

class SyncTraceSampler:
    def __init__(self, base_sample_rate: float = 0.1, error_sample_rate: float = 1.0):
        self.base_sample_rate = base_sample_rate
        self.error_sample_rate = error_sample_rate

    def should_sample(self, is_error: bool = False, is_slow: bool = False) -> bool:
        if is_error or is_slow:
            return random.random() < self.error_sample_rate
        return random.random() < self.base_sample_rate
