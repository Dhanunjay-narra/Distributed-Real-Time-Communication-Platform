"""Social Contact Graph and Discovery - Multi-Tier Cache Invalidation Coordinator.
"""
from typing import Set, Dict, List

class ContactsCacheInvalidationCoordinator:
    def __init__(self):
        self.tag_index: Dict[str, Set[str]] = {}

    def associate_tag(self, cache_key: str, tag: str):
        if tag not in self.tag_index:
            self.tag_index[tag] = set()
        self.tag_index[tag].add(cache_key)

    def invalidate_by_tag(self, tag: str) -> List[str]:
        keys = list(self.tag_index.pop(tag, set()))
        return keys
