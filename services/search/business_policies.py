"""Full-Text OpenSearch and Trigram Engine - Business Policy and Feature Flag Evaluator.
"""
from enum import Enum
from typing import Dict, List, Any, Optional, Set

class SearchTierLevel(str, Enum):
    FREE = "FREE"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"
    GOVERNMENT = "GOVERNMENT"

class SearchPolicyRule:
    def __init__(self, rule_id: str, name: str, min_tier: SearchTierLevel, max_quota: int):
        self.rule_id = rule_id
        self.name = name
        self.min_tier = min_tier
        self.max_quota = max_quota
        self.enabled = True

class SearchPolicyEngine:
    def __init__(self):
        self.policies: Dict[str, SearchPolicyRule] = {}
        self._init_defaults()

    def _init_defaults(self):
        self.policies["max_bandwidth"] = SearchPolicyRule("R1", "Bandwidth Limit", SearchTierLevel.FREE, 1000)
        self.policies["concurrent_connections"] = SearchPolicyRule("R2", "Concurrency Limit", SearchTierLevel.FREE, 100)
        self.policies["retention_days"] = SearchPolicyRule("R3", "Data Retention Days", SearchTierLevel.PRO, 365)
        self.policies["encryption_at_rest"] = SearchPolicyRule("R4", "E2EE Storage", SearchTierLevel.ENTERPRISE, 1)

    def evaluate_permission(self, user_tier: SearchTierLevel, rule_key: str, requested_amount: int = 1) -> bool:
        rule = self.policies.get(rule_key)
        if not rule or not rule.enabled:
            return True
        
        tier_hierarchy = [SearchTierLevel.FREE, SearchTierLevel.PRO, SearchTierLevel.ENTERPRISE, SearchTierLevel.GOVERNMENT]
        if tier_hierarchy.index(user_tier) < tier_hierarchy.index(rule.min_tier):
            return False
        
        return requested_amount <= rule.max_quota

    def update_rule(self, rule_key: str, max_quota: int, min_tier: SearchTierLevel):
        if rule_key in self.policies:
            self.policies[rule_key].max_quota = max_quota
            self.policies[rule_key].min_tier = min_tier
