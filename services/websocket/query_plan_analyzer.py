"""Distributed Gateway Connection Cluster - SQL Query Plan Analyzer and Index Hint Generator.
"""
from typing import Dict, List, Any

class WebsocketQueryPlanAnalyzer:
    def __init__(self):
        self.slow_query_log: List[Dict[str, Any]] = []

    def analyze_execution_plan(self, query: str, execution_time_ms: float) -> Dict[str, Any]:
        has_full_table_scan = "WHERE" not in query.upper() or "INDEX" not in query.upper()
        report = {
            "service": "websocket",
            "query": query,
            "latency_ms": execution_time_ms,
            "full_scan_detected": has_full_table_scan,
            "recommended_index": f"idx_websocket_optimized" if has_full_table_scan else None
        }
        if execution_time_ms > 100.0:
            self.slow_query_log.append(report)
        return report
