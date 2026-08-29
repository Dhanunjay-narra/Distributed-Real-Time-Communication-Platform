"""Multipart Chunking and Transcoding Pipeline - High-Speed Binary and JSON Serialization Buffers.
"""
import json, struct
from typing import Dict, Any, List, Optional

class MediaBinaryBuffer:
    def __init__(self):
        self.buffer = bytearray()

    def write_uint8(self, value: int):
        self.buffer.extend(struct.pack("!B", value))

    def write_uint16(self, value: int):
        self.buffer.extend(struct.pack("!H", value))

    def write_uint32(self, value: int):
        self.buffer.extend(struct.pack("!I", value))

    def write_string(self, text: str):
        raw = text.encode("utf-8")
        self.write_uint16(len(raw))
        self.buffer.extend(raw)

    def to_bytes(self) -> bytes:
        return bytes(self.buffer)

class MediaBinaryReader:
    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0

    def read_uint8(self) -> int:
        val = struct.unpack_from("!B", self.data, self.offset)[0]
        self.offset += 1
        return val

    def read_uint16(self) -> int:
        val = struct.unpack_from("!H", self.data, self.offset)[0]
        self.offset += 2
        return val

    def read_uint32(self) -> int:
        val = struct.unpack_from("!I", self.data, self.offset)[0]
        self.offset += 4
        return val

    def read_string(self) -> str:
        length = self.read_uint16()
        text = self.data[self.offset:self.offset + length].decode("utf-8")
        self.offset += length
        return text
