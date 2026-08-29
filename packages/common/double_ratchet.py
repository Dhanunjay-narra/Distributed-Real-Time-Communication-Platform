import os, hmac, hashlib
from typing import Dict, Tuple, Optional

class SymmetricKeyRatchet:
    def __init__(self, root_key: bytes):
        self.root_key = root_key
        self.chain_key = root_key
        self.step = 0

    def next_message_key(self) -> Tuple[bytes, bytes]:
        # Derives message key and next chain key via HKDF / HMAC-SHA256
        msg_key = hmac.new(self.chain_key, b"message-key", hashlib.sha256).digest()
        self.chain_key = hmac.new(self.chain_key, b"chain-key", hashlib.sha256).digest()
        self.step += 1
        return msg_key, self.chain_key

class DoubleRatchetSession:
    def __init__(self, shared_secret: bytes):
        self.root_key = shared_secret
        self.sending_ratchet = SymmetricKeyRatchet(hmac.new(shared_secret, b"sender", hashlib.sha256).digest())
        self.receiving_ratchet = SymmetricKeyRatchet(hmac.new(shared_secret, b"receiver", hashlib.sha256).digest())
        self.skipped_message_keys: Dict[Tuple[str, int], bytes] = {}

    def encrypt_payload(self, plaintext: bytes) -> Tuple[bytes, int]:
        msg_key, _ = self.sending_ratchet.next_message_key()
        # Simulated stream cipher XOR with derived keystream
        keystream = hashlib.sha256(msg_key + b"stream").digest()
        padded_stream = (keystream * ((len(plaintext) // len(keystream)) + 1))[:len(plaintext)]
        ciphertext = bytes(a ^ b for a, b in zip(plaintext, padded_stream))
        return ciphertext, self.sending_ratchet.step

    def decrypt_payload(self, ciphertext: bytes, step: int) -> bytes:
        msg_key, _ = self.receiving_ratchet.next_message_key()
        keystream = hashlib.sha256(msg_key + b"stream").digest()
        padded_stream = (keystream * ((len(ciphertext) // len(keystream)) + 1))[:len(ciphertext)]
        return bytes(a ^ b for a, b in zip(ciphertext, padded_stream))
