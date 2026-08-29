"""Identity and Multi-Factor Device Authentication - Attribute-Based Access Control (ABAC) Policy Evaluator.
"""
from typing import Dict, Any, List

class AuthABACEvaluator:
    def __init__(self):
        self.rules: List[Dict[str, Any]] = []

    def add_policy_rule(self, subject_attr: str, action: str, resource_attr: str, allow: bool = True):
        self.rules.append({
            "subject_attr": subject_attr,
            "action": action,
            "resource_attr": resource_attr,
            "allow": allow
        })

    def evaluate(self, subject: Dict[str, Any], action: str, resource: Dict[str, Any]) -> bool:
        for rule in self.rules:
            if rule["action"] == action:
                sub_match = subject.get(rule["subject_attr"]) == rule.get("subject_attr_val", True)
                res_match = resource.get(rule["resource_attr"]) == rule.get("resource_attr_val", True)
                if sub_match and res_match:
                    return rule["allow"]
        return True
