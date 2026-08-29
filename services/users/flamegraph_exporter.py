"""User Profiles and Presence Status - Flamegraph Stack Trace and CPU Profiling Exporter.
"""
import time
from typing import List, Dict, Any

class UsersFlamegraphExporter:
    def __init__(self):
        self.samples: List[Dict[str, Any]] = []

    def record_stack_sample(self, stack_frames: List[str], duration_us: int):
        self.samples.append({
            "stack": ";".join(stack_frames),
            "duration": duration_us,
            "timestamp": time.time()
        })
        if len(self.samples) > 5000:
            self.samples.pop(0)

    def export_folded_stacks(self) -> str:
        lines = []
        for s in self.samples:
            lines.append(f"{s['stack']} {s['duration']}")
        return "\n".join(lines)
