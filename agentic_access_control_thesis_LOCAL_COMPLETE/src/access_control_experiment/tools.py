from __future__ import annotations

from .environment import SyntheticEnvironment
from .models import Case, Detection


class AgentTools:
    """Bounded read tools available to the post-detection agent."""

    @staticmethod
    def gather_context(case: Case, env: SyntheticEnvironment, detection: Detection) -> dict:
        return {
            "case_id": case.case_id,
            "policy_id": case.policy_id,
            "detector_evidence": detection.evidence,
            "identity": env.identity,
            "context": env.context,
            "exceptions": env.exceptions,
            "context_complete": case.agent_context_complete,
        }
