"""Safety Scanning and Sanctions Queue - Cryptographic Hash Chain Verifier.
"""
import hashlib
from typing import List, Dict, Any

class ModerationHashChainVerifier:
    @staticmethod
    def verify_chain(blocks: List[Dict[str, Any]]) -> bool:
        for i in range(1, len(blocks)):
            prev = blocks[i - 1]
            curr = blocks[i]
            if curr.get("previous_hash") != prev.get("hash"):
                return False
        return True
