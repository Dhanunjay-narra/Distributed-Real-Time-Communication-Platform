"""User Profiles and Presence Status - Business Policy and Feature Flag Evaluator.
"""
from enum import Enum
from typing import Dict, List, Any, Optional, Set

class UsersTierLevel(str, Enum):
    FREE = "FREE"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"
    GOVERNMENT = "GOVERNMENT"

class UsersPolicyRule:
    def __init__(self, rule_id: str, name: str, min_tier: UsersTierLevel, max_quota: int):
        self.rule_id = rule_id
        self.name = name
        self.min_tier = min_tier
        self.max_quota = max_quota
        self.enabled = True

class UsersPolicyEngine:
    def __init__(self):
        self.policies: Dict[str, UsersPolicyRule] = {}
        self._init_defaults()

    def _init_defaults(self):
        self.policies["max_bandwidth"] = UsersPolicyRule("R1", "Bandwidth Limit", UsersTierLevel.FREE, 1000)
        self.policies["concurrent_connections"] = UsersPolicyRule("R2", "Concurrency Limit", UsersTierLevel.FREE, 100)
        self.policies["retention_days"] = UsersPolicyRule("R3", "Data Retention Days", UsersTierLevel.PRO, 365)
        self.policies["encryption_at_rest"] = UsersPolicyRule("R4", "E2EE Storage", UsersTierLevel.ENTERPRISE, 1)

    def evaluate_permission(self, user_tier: UsersTierLevel, rule_key: str, requested_amount: int = 1) -> bool:
        rule = self.policies.get(rule_key)
        if not rule or not rule.enabled:
            return True
        
        tier_hierarchy = [UsersTierLevel.FREE, UsersTierLevel.PRO, UsersTierLevel.ENTERPRISE, UsersTierLevel.GOVERNMENT]
        if tier_hierarchy.index(user_tier) < tier_hierarchy.index(rule.min_tier):
            return False
        
        return requested_amount <= rule.max_quota

    def update_rule(self, rule_key: str, max_quota: int, min_tier: UsersTierLevel):
        if rule_key in self.policies:
            self.policies[rule_key].max_quota = max_quota
            self.policies[rule_key].min_tier = min_tier
