from __future__ import annotations

from datetime import date
from .models import Case, Detection


class RuleEngine:
    """Deterministic detector. It intentionally ignores post-detection exceptions."""

    def __init__(self, as_of_date: str):
        self.as_of = date.fromisoformat(as_of_date)

    def detect(self, case: Case) -> Detection:
        i = case.identity
        c = case.context
        policy = case.policy_id
        triggered = False
        evidence: dict = {}

        if policy == "P1":
            expiry = date.fromisoformat(c["temporary_access_expires_on"])
            target = c["temporary_access_role"]
            triggered = target in i.get("roles", []) and expiry < self.as_of
            evidence = {"target_role": target, "expiry": str(expiry), "as_of": str(self.as_of)}

        elif policy == "P2":
            target = c["project_role"]
            triggered = target in i.get("roles", []) and c.get("project_status") == "ended"
            evidence = {"target_role": target, "project_status": c.get("project_status")}

        elif policy == "P3":
            target = c["privileged_role"]
            triggered = target in i.get("roles", []) and not bool(c.get("baseline_privileged_authorized", False))
            evidence = {"target_role": target, "baseline_authorized": c.get("baseline_privileged_authorized", False)}

        elif policy == "P4":
            triggered = i.get("employment_status") == "terminated" and bool(i.get("account_enabled", False))
            evidence = {"employment_status": i.get("employment_status"), "account_enabled": i.get("account_enabled")}

        elif policy == "P5":
            threshold = int(c.get("inactivity_threshold_days", 90))
            inactive = int(i.get("inactive_days", 0))
            triggered = bool(i.get("account_enabled", False)) and inactive > threshold
            evidence = {"inactive_days": inactive, "threshold_days": threshold, "identity_type": i.get("identity_type")}

        elif policy == "P6":
            roles = set(i.get("roles", []))
            required = set(c.get("sod_conflicting_roles", ["requester", "approver"]))
            triggered = required.issubset(roles)
            evidence = {"roles": sorted(roles), "conflicting_roles": sorted(required)}

        else:
            raise ValueError(f"Unknown policy: {policy}")

        return Detection(case_id=case.case_id, policy_id=policy, triggered=triggered, evidence=evidence)
