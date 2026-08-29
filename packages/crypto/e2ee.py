import hashlib
import hmac

class DoubleRatchetSession:
    def __init__(self, shared_secret: bytes):
        self.root_key = shared_secret
        self.chain_key = hashlib.sha256(shared_secret).digest()
        self.message_number = 0

    def step_ratchet(self, payload: bytes) -> bytes:
        self.message_number += 1
        derived = hmac.new(self.chain_key, f"msg-{self.message_number}".encode(), hashlib.sha256).digest()
        self.chain_key = hashlib.sha256(self.chain_key + derived).digest()
        return derived
