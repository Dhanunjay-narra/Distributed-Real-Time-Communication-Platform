import copy
from typing import Dict, Any

class VectorClock:
    def __init__(self, clock_dict: Dict[str, int] = None):
        self.clock: Dict[str, int] = copy.deepcopy(clock_dict or {})

    def increment(self, node_id: str) -> None:
        self.clock[node_id] = self.clock.get(node_id, 0) + 1

    def get(self, node_id: str) -> int:
        return self.clock.get(node_id, 0)

    def merge(self, other: 'VectorClock') -> 'VectorClock':
        all_nodes = set(self.clock.keys()).union(set(other.clock.keys()))
        merged = {node: max(self.get(node), other.get(node)) for node in all_nodes}
        return VectorClock(merged)

    def is_causally_newer(self, other: 'VectorClock') -> bool:
        greater_or_equal = True
        strictly_greater = False
        all_nodes = set(self.clock.keys()).union(set(other.clock.keys()))

        for node in all_nodes:
            v_self = self.get(node)
            v_other = other.get(node)
            if v_self < v_other:
                greater_or_equal = False
            elif v_self > v_other:
                strictly_greater = True

        return greater_or_equal and strictly_greater

    def is_concurrent_with(self, other: 'VectorClock') -> bool:
        return not self.is_causally_newer(other) and not other.is_causally_newer(self) and self.clock != other.clock

    def to_dict(self) -> Dict[str, int]:
        return dict(self.clock)
