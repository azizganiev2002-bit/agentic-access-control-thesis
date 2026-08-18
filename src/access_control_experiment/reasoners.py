from __future__ import annotations

import json
import os
import random
from abc import ABC, abstractmethod
from typing import Any

from .models import Action, ActionType, AgentDecision, Case


class Reasoner(ABC):
    name: str

    @abstractmethod
    def recommend(self, case: Case, policy: dict[str, Any], context: dict[str, Any]) -> AgentDecision:
        raise NotImplementedError


class MockReasoner(Reasoner):
    """Local test backend. Never use mock runs as the thesis's final AI results."""

    name = "mock"

    def __init__(self, error_rate: float = 0.0, seed: int = 42):
        self.error_rate = error_rate
        self.rng = random.Random(seed)

    def recommend(self, case: Case, policy: dict[str, Any], context: dict[str, Any]) -> AgentDecision:
        if not context.get("context_complete", True):
            return AgentDecision(
                action=Action(type=ActionType.NO_ACTION),
                needs_human_review=True,
                rationale="Context is incomplete; escalation is required.",
            )

        active_exception = any(bool(e.get("valid")) and e.get("policy_id") == case.policy_id for e in context["exceptions"])
        if active_exception:
            return AgentDecision(
                action=Action(type=ActionType.NO_ACTION),
                needs_human_review=False,
                rationale="A valid exception applies; no remediation is recommended.",
            )

        expected_type = ActionType(policy["expected_action"])
        target = _policy_target(case, expected_type)
        decision = AgentDecision(
            action=Action(type=expected_type, target=target),
            needs_human_review=False,
            rationale="The observed state matches the policy trigger and no valid exception was found.",
        )

        if self.error_rate > 0 and self.rng.random() < self.error_rate:
            decision = self._inject_plausible_error(case, decision)
        return decision

    def _inject_plausible_error(self, case: Case, decision: AgentDecision) -> AgentDecision:
        # Prefer wrong-target errors on low-impact role-removal cases so the A3
        # guardrails can be tested without bypassing the policy/action allowlist.
        roles = list(case.identity.get("roles", []))
        if decision.action.type in {ActionType.REMOVE_TEMP_ACCESS, ActionType.REMOVE_PROJECT_ACCESS}:
            distractors = [r for r in roles if r != decision.action.target]
            if distractors:
                return AgentDecision(
                    action=Action(type=decision.action.type, target=self.rng.choice(distractors)),
                    needs_human_review=False,
                    rationale="Mock backend intentionally selected an incorrect but syntactically valid target.",
                )
        return AgentDecision(
            action=Action(type=ActionType.NO_ACTION),
            needs_human_review=False,
            rationale="Mock backend intentionally produced an incorrect no-action recommendation.",
        )


class OpenAIReasoner(Reasoner):
    """Structured-output LLM backend for the actual experimental agent."""

    name = "openai"

    def __init__(self, model: str | None = None):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install the openai package before using --backend openai") from exc

        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5.6")
        self.client = OpenAI()

    def recommend(self, case: Case, policy: dict[str, Any], context: dict[str, Any]) -> AgentDecision:
        system = (
            "You are a constrained access-control remediation agent in a research experiment. "
            "The deterministic detector has already triggered, but a trigger is not proof that remediation is appropriate. "
            "Inspect the supplied identity context and valid exceptions. Recommend exactly one allowed action. "
            "If a valid exception means no change should occur, choose NO_ACTION. "
            "If context is insufficient or ambiguous, set needs_human_review=true and choose NO_ACTION. "
            "Never invent identities, roles, exceptions, or evidence. Do not produce a confidence score."
        )
        payload = {
            "policy": policy,
            "case_description": case.description,
            "available_actions": [a.value for a in ActionType],
            "observed_context": context,
        }
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(payload, sort_keys=True)},
            ],
            text_format=AgentDecision,
        )
        if response.output_parsed is None:
            raise RuntimeError("Model returned no parseable AgentDecision")
        return response.output_parsed


def _policy_target(case: Case, action_type: ActionType) -> str | None:
    c = case.context
    if action_type == ActionType.REMOVE_TEMP_ACCESS:
        return c.get("temporary_access_role")
    if action_type == ActionType.REMOVE_PROJECT_ACCESS:
        return c.get("project_role")
    if action_type == ActionType.REMOVE_PRIVILEGED_ACCESS:
        return c.get("privileged_role")
    if action_type == ActionType.REMOVE_SOD_ROLE:
        return c.get("preferred_sod_role_to_remove", "approver")
    return None
