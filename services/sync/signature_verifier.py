"""Vector Clock Replication and Offline Recovery - Cryptographic Digest and Signature Verifier.
"""
import hmac, hashlib
from typing import Optional

class SyncSignatureVerifier:
    def __init__(self, signing_secret: str = "chatbot-internal-service-token-secret"):
        self.secret = signing_secret.encode("utf-8")

    def sign_payload(self, raw_payload: str) -> str:
        return hmac.new(self.secret, raw_payload.encode("utf-8"), hashlib.sha256).hexdigest()

    def verify_signature(self, raw_payload: str, signature: str) -> bool:
        expected = self.sign_payload(raw_payload)
        return hmac.compare_digest(expected, signature)
