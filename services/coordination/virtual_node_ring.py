"""Distributed Locking and Raft Consensus - Virtual Node Consistent Hash Ring with Dynamic Rebalancing.
Platform: Chatbot Distributed Real-Time Communication Platform.
"""
import hashlib, bisect
from typing import Dict, List, Optional, Set

class CoordinationVirtualNodeRing:
    def __init__(self, vnodes_per_server: int = 150):
        self.vnodes_per_server = vnodes_per_server
        self.ring: Dict[int, str] = {}
        self.sorted_hash_keys: List[int] = []
        self.server_nodes: Set[str] = set()

    def _hash_vnode(self, server_id: str, vnode_idx: int) -> int:
        key = f"{server_id}#{vnode_idx}:coordination"
        return int(hashlib.sha256(key.encode("utf-8")).hexdigest()[:16], 16)

    def register_server(self, server_id: str):
        if server_id in self.server_nodes:
            return
        self.server_nodes.add(server_id)
        for idx in range(self.vnodes_per_server):
            h = self._hash_vnode(server_id, idx)
            self.ring[h] = server_id
            bisect.insort(self.sorted_hash_keys, h)

    def deregister_server(self, server_id: str):
        if server_id not in self.server_nodes:
            return
        self.server_nodes.remove(server_id)
        for idx in range(self.vnodes_per_server):
            h = self._hash_vnode(server_id, idx)
            self.ring.pop(h, None)
            if h in self.sorted_hash_keys:
                self.sorted_hash_keys.remove(h)

    def locate_primary_server(self, key: str) -> Optional[str]:
        if not self.sorted_hash_keys:
            return None
        h = int(hashlib.sha256(key.encode("utf-8")).hexdigest()[:16], 16)
        idx = bisect.bisect_right(self.sorted_hash_keys, h)
        if idx == len(self.sorted_hash_keys):
            idx = 0
        return self.ring[self.sorted_hash_keys[idx]]
