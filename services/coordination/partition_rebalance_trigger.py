"""Distributed Locking and Raft Consensus - Partition Rebalance Trigger and Health Watcher.
"""
import time
from typing import Dict, Any

class CoordinationPartitionRebalanceTrigger:
    def __init__(self, threshold_seconds: float = 30.0):
        self.threshold = threshold_seconds
        self.last_heartbeat = time.time()

    def check_trigger_condition(self, node_heartbeat: float) -> bool:
        return (time.time() - node_heartbeat) > self.threshold
