"""WebRTC Voice/Video Signaling Mesh - Weighted Round-Robin Load Balancer and Replica Selector.
"""
from typing import List, Dict, Any, Optional

class CallsReplicaNode:
    def __init__(self, node_id: str, host: str, port: int, weight: int = 1):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.weight = weight
        self.active_connections = 0
        self.is_healthy = True

class CallsLoadBalancer:
    def __init__(self):
        self.replicas: List[CallsReplicaNode] = []
        self._current_index = 0

    def add_replica(self, node_id: str, host: str, port: int, weight: int = 1):
        self.replicas.append(CallsReplicaNode(node_id, host, port, weight))

    def select_next_replica(self) -> Optional[CallsReplicaNode]:
        healthy_nodes = [n for n in self.replicas if n.is_healthy]
        if not healthy_nodes:
            return None
        node = healthy_nodes[self._current_index % len(healthy_nodes)]
        self._current_index += 1
        return node
