"""Social Contact Graph and Discovery - High-Throughput Ring Buffer Stream Processor.
"""
from typing import List, Optional, Any

class ContactsRingBuffer:
    def __init__(self, capacity: int = 1024):
        self.capacity = capacity
        self.buffer: List[Optional[Any]] = [None] * capacity
        self.head = 0
        self.tail = 0
        self.size = 0

    def push(self, item: Any):
        self.buffer[self.tail] = item
        self.tail = (self.tail + 1) % self.capacity
        if self.size < self.capacity:
            self.size += 1
        else:
            self.head = (self.head + 1) % self.capacity

    def pop(self) -> Optional[Any]:
        if self.size == 0:
            return None
        item = self.buffer[self.head]
        self.buffer[self.head] = None
        self.head = (self.head + 1) % self.capacity
        self.size -= 1
        return item
