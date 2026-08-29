"""Kafka Stream Partitioning and Sagas - Merkle Tree Audit Ledger and Proof Generator.
Platform: Chatbot Distributed Real-Time Communication Platform.
"""
import hashlib
from typing import List, Optional

class EventsMerkleNode:
    def __init__(self, left: Optional["EventsMerkleNode"], right: Optional["EventsMerkleNode"], hash_value: str):
        self.left = left
        self.right = right
        self.hash_value = hash_value

class EventsMerkleTree:
    def __init__(self):
        self.leaves: List[str] = []
        self.root: Optional[EventsMerkleNode] = None

    def add_leaf(self, data: str):
        h = hashlib.sha256(data.encode("utf-8")).hexdigest()
        self.leaves.append(h)
        self.rebuild_tree()

    def rebuild_tree(self):
        if not self.leaves:
            self.root = None
            return
        nodes = [EventsMerkleNode(None, None, h) for h in self.leaves]
        while len(nodes) > 1:
            if len(nodes) % 2 != 0:
                nodes.append(nodes[-1])
            new_level = []
            for i in range(0, len(nodes), 2):
                combined = nodes[i].hash_value + nodes[i + 1].hash_value
                parent_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()
                parent_node = EventsMerkleNode(nodes[i], nodes[i + 1], parent_hash)
                new_level.append(parent_node)
            nodes = new_level
        self.root = nodes[0]

    def get_root_hash(self) -> Optional[str]:
        return self.root.hash_value if self.root else None
