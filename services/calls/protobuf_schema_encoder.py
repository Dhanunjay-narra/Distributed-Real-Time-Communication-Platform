"""WebRTC Voice/Video Signaling Mesh - Schema Encoders and Protobuf Wire Formatters.
"""
import json, base64
from typing import Dict, Any

class CallsEnvelopeBuilder:
    @staticmethod
    def build_envelope(topic: str, event_type: str, data: Dict[str, Any], correlation_id: str) -> bytes:
        envelope = {
            "meta": {
                "topic": topic,
                "event_type": event_type,
                "correlation_id": correlation_id,
                "version": "1.0",
                "service": "calls"
            },
            "payload": data
        }
        return json.dumps(envelope).encode("utf-8")

    @staticmethod
    def parse_envelope(raw_bytes: bytes) -> Dict[str, Any]:
        return json.loads(raw_bytes.decode("utf-8"))
