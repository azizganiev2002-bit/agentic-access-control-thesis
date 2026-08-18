from __future__ import annotations

from typing import Any
from .environment import SyntheticEnvironment
from .models import AgentDecision, GuardrailDecision, Impact


class GuardrailEngine:
    def __init__(self, actions: dict[str, Any]):
        self.actions = actions

    def evaluate(self, policy_id: str, decision: AgentDecision, env: SyntheticEnvironment, context_complete: bool) -> GuardrailDecision:
        reasons: list[str] = []
        action_name = decision.action.type.value
        cfg = self.actions[action_name]

        if decision.needs_human_review:
            reasons.append("agent_requested_human_review")

        if not context_complete:
            reasons.append("incomplete_context")

        if env.has_active_exception(policy_id):
            reasons.append("valid_exception")

        if policy_id not in cfg.get("allowed_for_policies", []):
            reasons.append("action_not_allowed_for_policy")

        if cfg.get("impact") not in {Impact.LOW.value, Impact.NONE.value}:
            reasons.append("high_impact_action")

        # NO_ACTION is autonomously acceptable only if a valid exception exists.
        if action_name == "NO_ACTION" and not env.has_active_exception(policy_id):
            reasons.append("no_action_without_exception_requires_review")

        # For role-removal actions, the proposed target must actually be assigned.
        if action_name.startswith("REMOVE_") and action_name != "REMOVE_SOD_ROLE":
            target = decision.action.target
            if not target or target not in env.identity.get("roles", []):
                reasons.append("invalid_or_missing_target")

        if action_name == "REMOVE_SOD_ROLE":
            target = decision.action.target
            if not target or target not in env.identity.get("roles", []):
                reasons.append("invalid_or_missing_target")

        return GuardrailDecision(autonomous_allowed=(len(reasons) == 0), reasons=reasons)
