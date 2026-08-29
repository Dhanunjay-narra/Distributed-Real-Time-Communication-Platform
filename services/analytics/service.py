import time
from typing import Dict, Any, List

class AnalyticsEngine:
    def __init__(self):
        self.total_messages_processed = 0
        self.active_users_daily = set()
        self.latencies_ms: List[float] = []

    def record_message(self, user_id: str, latency_ms: float = 15.0):
        self.total_messages_processed += 1
        self.active_users_daily.add(user_id)
        self.latencies_ms.append(latency_ms)

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        avg_lat = sum(self.latencies_ms) / len(self.latencies_ms) if self.latencies_ms else 0.0
        return {
            "total_messages": self.total_messages_processed,
            "daily_active_users": len(self.active_users_daily),
            "average_latency_ms": round(avg_lat, 2),
            "system_health": "OPTIMAL"
        }

analytics_engine = AnalyticsEngine()
