"""Conversation Partitioning and Channels - Compact Merkle Audit Proof Verifier.
Platform: Chatbot Distributed Real-Time Communication Platform.
"""
import hashlib
from typing import List, Tuple

class ConversationsMerkleCompactProver:
    @staticmethod
    def verify_inclusion_proof(leaf_data: str, proof_path: List[Tuple[str, str]], expected_root: str) -> bool:
        current_hash = hashlib.sha256(leaf_data.encode("utf-8")).hexdigest()
        for sibling_hash, direction in proof_path:
            if direction == "left":
                combined = sibling_hash + current_hash
            else:
                combined = current_hash + sibling_hash
            current_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()
        return current_hash == expected_root
