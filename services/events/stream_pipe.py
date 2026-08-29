"""Kafka Stream Partitioning and Sagas - Stream Processing Pipe and Delta Filter.
"""
from typing import List, Dict, Any, Callable, Optional

class EventsStreamPipe:
    def __init__(self):
        self.filters: List[Callable[[Dict[str, Any]], bool]] = []
        self.transformers: List[Callable[[Dict[str, Any]], Dict[str, Any]]] = []

    def add_filter(self, predicate: Callable[[Dict[str, Any]], bool]):
        self.filters.append(predicate)

    def add_transformer(self, transform_fn: Callable[[Dict[str, Any]], Dict[str, Any]]):
        self.transformers.append(transform_fn)

    def process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for f in self.filters:
            if not f(item):
                return None
        
        current = item
        for t in self.transformers:
            current = t(current)
        return current

    def process_batch(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for item in items:
            res = self.process_item(item)
            if res is not None:
                results.append(res)
        return results
