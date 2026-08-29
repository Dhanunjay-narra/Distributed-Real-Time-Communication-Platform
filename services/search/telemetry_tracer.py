"""Full-Text OpenSearch and Trigram Engine - Distributed Telemetry, Tracing and Performance Profiler.
"""
import time
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class SearchSpan(BaseModel):
    span_id: str
    trace_id: str
    operation: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: float = 0.0
    tags: Dict[str, str] = Field(default_factory=dict)
    logs: List[Dict[str, Any]] = Field(default_factory=list)

class SearchTracer:
    def __init__(self):
        self.active_spans: Dict[str, SearchSpan] = {}
        self.completed_spans: List[SearchSpan] = []

    def start_span(self, trace_id: str, operation: str, tags: Optional[Dict[str, str]] = None) -> SearchSpan:
        import uuid
        span_id = str(uuid.uuid4())
        span = SearchSpan(
            span_id=span_id,
            trace_id=trace_id,
            operation=operation,
            start_time=time.time(),
            tags=tags or {}
        )
        self.active_spans[span_id] = span
        return span

    def end_span(self, span_id: str) -> Optional[SearchSpan]:
        span = self.active_spans.pop(span_id, None)
        if span:
            span.end_time = time.time()
            span.duration_ms = (span.end_time - span.start_time) * 1000
            self.completed_spans.append(span)
            if len(self.completed_spans) > 2000:
                self.completed_spans.pop(0)
            return span
        return None

    def get_span_stats(self) -> Dict[str, Any]:
        if not self.completed_spans:
            return {"service": "search", "avg_duration_ms": 0.0, "total_spans": 0}
        durations = [s.duration_ms for s in self.completed_spans]
        return {
            "service": "search",
            "avg_duration_ms": sum(durations) / len(durations),
            "max_duration_ms": max(durations),
            "total_spans": len(durations)
        }
