from __future__ import annotations

from .models import Action, AgentDecision, Case


class SimulatedHumanReviewer:
    """Deterministic reference reviewer based on pre-established ground truth."""

    def decide(self, case: Case, recommendation: AgentDecision | None = None) -> tuple[Action, str]:
        expected = case.ground_truth.expected_action
        if recommendation is None:
            return expected, "human_resolved_from_ground_truth"

        if recommendation.action == expected:
            return recommendation.action, "approved_agent_recommendation"

        return expected, "rejected_agent_recommendation_and_applied_ground_truth"
