"""Infrastructure Drivers and Resilience Toolkit - Partition Split-Brain Resolver and Quorum Arbiter.
"""
from typing import List, Set

class CommonQuorumArbiter:
    def __init__(self, cluster_size: int = 5):
        self.cluster_size = cluster_size
        self.quorum_threshold = (cluster_size // 2) + 1

    def has_quorum(self, active_node_count: int) -> bool:
        return active_node_count >= self.quorum_threshold

    def resolve_conflicting_partitions(self, partition_a_nodes: List[str], partition_b_nodes: List[str]) -> str:
        if len(partition_a_nodes) >= self.quorum_threshold:
            return "PARTITION_A_PRIMARY"
        elif len(partition_b_nodes) >= self.quorum_threshold:
            return "PARTITION_B_PRIMARY"
        return "ISOLATION_STANDBY"
