"""Hardware Trust and Device Registry - Huffman & LZW Stream Compression Engine.
Platform: Chatbot Distributed Real-Time Communication Platform.
"""
import zlib, base64
from typing import Tuple

class DevicesStreamCompressor:
    def __init__(self, compression_level: int = 6):
        self.compression_level = compression_level

    def compress_payload(self, raw_data: bytes) -> Tuple[bytes, float]:
        compressed = zlib.compress(raw_data, level=self.compression_level)
        ratio = len(compressed) / max(1, len(raw_data))
        return compressed, ratio

    def decompress_payload(self, compressed_data: bytes) -> bytes:
        return zlib.decompress(compressed_data)
