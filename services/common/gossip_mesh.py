"""Infrastructure Drivers and Resilience Toolkit - Peer-to-Peer Gossip Mesh Protocol and Node Discovery.
Platform: Chatbot Distributed Real-Time Communication Platform.
"""
import time, random
from typing import Dict, List, Any, Optional, Set

class CommonGossipNode:
    def __init__(self, node_id: str, address: str, heartbeat: int = 0):
        self.node_id = node_id
        self.address = address
        self.heartbeat = heartbeat
        self.last_seen = time.time()
        self.generation = 1

class CommonGossipMesh:
    def __init__(self, local_node_id: str):
        self.local_node_id = local_node_id
        self.peers: Dict[str, CommonGossipNode] = {}
        self.heartbeat_counter = 0

    def add_peer(self, node_id: str, address: str):
        if node_id != self.local_node_id:
            self.peers[node_id] = CommonGossipNode(node_id, address)

    def increment_local_heartbeat(self):
        self.heartbeat_counter += 1

    def prepare_gossip_digest(self) -> Dict[str, Any]:
        return {
            "sender": self.local_node_id,
            "heartbeat": self.heartbeat_counter,
            "peers": {p_id: p.heartbeat for p_id, p in self.peers.items()},
            "timestamp": time.time()
        }

    def merge_gossip_digest(self, digest: Dict[str, Any]):
        sender_id = digest.get("sender")
        if sender_id and sender_id in self.peers:
            node = self.peers[sender_id]
            node.heartbeat = max(node.heartbeat, digest.get("heartbeat", 0))
            node.last_seen = time.time()
