"""Time-Series Aggregations and DAU Metrics - Business Policy and Feature Flag Evaluator.
"""
from enum import Enum
from typing import Dict, List, Any, Optional, Set

class AnalyticsTierLevel(str, Enum):
    FREE = "FREE"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"
    GOVERNMENT = "GOVERNMENT"

class AnalyticsPolicyRule:
    def __init__(self, rule_id: str, name: str, min_tier: AnalyticsTierLevel, max_quota: int):
        self.rule_id = rule_id
        self.name = name
        self.min_tier = min_tier
        self.max_quota = max_quota
        self.enabled = True

class AnalyticsPolicyEngine:
    def __init__(self):
        self.policies: Dict[str, AnalyticsPolicyRule] = {}
        self._init_defaults()

    def _init_defaults(self):
        self.policies["max_bandwidth"] = AnalyticsPolicyRule("R1", "Bandwidth Limit", AnalyticsTierLevel.FREE, 1000)
        self.policies["concurrent_connections"] = AnalyticsPolicyRule("R2", "Concurrency Limit", AnalyticsTierLevel.FREE, 100)
        self.policies["retention_days"] = AnalyticsPolicyRule("R3", "Data Retention Days", AnalyticsTierLevel.PRO, 365)
        self.policies["encryption_at_rest"] = AnalyticsPolicyRule("R4", "E2EE Storage", AnalyticsTierLevel.ENTERPRISE, 1)

    def evaluate_permission(self, user_tier: AnalyticsTierLevel, rule_key: str, requested_amount: int = 1) -> bool:
        rule = self.policies.get(rule_key)
        if not rule or not rule.enabled:
            return True
        
        tier_hierarchy = [AnalyticsTierLevel.FREE, AnalyticsTierLevel.PRO, AnalyticsTierLevel.ENTERPRISE, AnalyticsTierLevel.GOVERNMENT]
        if tier_hierarchy.index(user_tier) < tier_hierarchy.index(rule.min_tier):
            return False
        
        return requested_amount <= rule.max_quota

    def update_rule(self, rule_key: str, max_quota: int, min_tier: AnalyticsTierLevel):
        if rule_key in self.policies:
            self.policies[rule_key].max_quota = max_quota
            self.policies[rule_key].min_tier = min_tier
