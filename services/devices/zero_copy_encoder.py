"""Hardware Trust and Device Registry - Zero-Copy Binary Buffer Encoder.
"""
import struct
from typing import List

class DevicesZeroCopyEncoder:
    def __init__(self):
        self.raw_data = bytearray()

    def pack_header(self, magic: int, version: int, payload_len: int):
        self.raw_data.extend(struct.pack("!HHI", magic, version, payload_len))

    def append_raw_bytes(self, chunk: bytes):
        self.raw_data.extend(chunk)

    def export_buffer(self) -> bytes:
        return bytes(self.raw_data)
