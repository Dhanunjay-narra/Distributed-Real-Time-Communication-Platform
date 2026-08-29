"""Ephemeral Mesh and Activity Streams - Business Policy and Feature Flag Evaluator.
"""
from enum import Enum
from typing import Dict, List, Any, Optional, Set

class PresenceTierLevel(str, Enum):
    FREE = "FREE"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"
    GOVERNMENT = "GOVERNMENT"

class PresencePolicyRule:
    def __init__(self, rule_id: str, name: str, min_tier: PresenceTierLevel, max_quota: int):
        self.rule_id = rule_id
        self.name = name
        self.min_tier = min_tier
        self.max_quota = max_quota
        self.enabled = True

class PresencePolicyEngine:
    def __init__(self):
        self.policies: Dict[str, PresencePolicyRule] = {}
        self._init_defaults()

    def _init_defaults(self):
        self.policies["max_bandwidth"] = PresencePolicyRule("R1", "Bandwidth Limit", PresenceTierLevel.FREE, 1000)
        self.policies["concurrent_connections"] = PresencePolicyRule("R2", "Concurrency Limit", PresenceTierLevel.FREE, 100)
        self.policies["retention_days"] = PresencePolicyRule("R3", "Data Retention Days", PresenceTierLevel.PRO, 365)
        self.policies["encryption_at_rest"] = PresencePolicyRule("R4", "E2EE Storage", PresenceTierLevel.ENTERPRISE, 1)

    def evaluate_permission(self, user_tier: PresenceTierLevel, rule_key: str, requested_amount: int = 1) -> bool:
        rule = self.policies.get(rule_key)
        if not rule or not rule.enabled:
            return True
        
        tier_hierarchy = [PresenceTierLevel.FREE, PresenceTierLevel.PRO, PresenceTierLevel.ENTERPRISE, PresenceTierLevel.GOVERNMENT]
        if tier_hierarchy.index(user_tier) < tier_hierarchy.index(rule.min_tier):
            return False
        
        return requested_amount <= rule.max_quota

    def update_rule(self, rule_key: str, max_quota: int, min_tier: PresenceTierLevel):
        if rule_key in self.policies:
            self.policies[rule_key].max_quota = max_quota
            self.policies[rule_key].min_tier = min_tier
