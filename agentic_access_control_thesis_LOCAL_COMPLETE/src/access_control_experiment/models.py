from __future__ import annotations

from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    NO_ACTION = "NO_ACTION"
    REMOVE_TEMP_ACCESS = "REMOVE_TEMP_ACCESS"
    REMOVE_PROJECT_ACCESS = "REMOVE_PROJECT_ACCESS"
    REMOVE_PRIVILEGED_ACCESS = "REMOVE_PRIVILEGED_ACCESS"
    DISABLE_ACCOUNT = "DISABLE_ACCOUNT"
    REMOVE_SOD_ROLE = "REMOVE_SOD_ROLE"


class Impact(str, Enum):
    NONE = "none"
    LOW = "low"
    HIGH = "high"


class Severity(str, Enum):
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class Action(BaseModel):
    type: ActionType
    target: str | None = None


class GroundTruth(BaseModel):
    detector_should_trigger: bool
    is_violation: bool
    expected_action: Action
    wrong_action_severity: Severity


class Case(BaseModel):
    case_id: str
    scenario_family: str
    variant: Literal["clear", "exception", "context"]
    description: str
    policy_id: str
    identity: dict[str, Any]
    context: dict[str, Any] = Field(default_factory=dict)
    exceptions: list[dict[str, Any]] = Field(default_factory=list)
    agent_context_complete: bool = True
    ground_truth: GroundTruth


class Detection(BaseModel):
    case_id: str
    policy_id: str
    triggered: bool
    evidence: dict[str, Any]


class AgentDecision(BaseModel):
    action: Action
    needs_human_review: bool = False
    rationale: str


class GuardrailDecision(BaseModel):
    autonomous_allowed: bool
    reasons: list[str] = Field(default_factory=list)


class RunRecord(BaseModel):
    run_id: str
    case_id: str
    scenario_family: str
    variant: str
    policy_id: str
    autonomy: Literal["A1", "A2", "A3"]
    repetition: int
    backend: str
    detector_triggered: bool
    agent_action: str | None
    agent_target: str | None
    agent_rationale: str | None
    guardrail_allowed: bool | None
    guardrail_reasons: list[str] = Field(default_factory=list)
    human_intervention: bool
    human_decision: str | None
    executed_action: str | None
    executed_target: str | None
    executed_by: str | None
    inappropriate_action_executed: bool
    final_state_correct: bool
    remediation_success: bool | None
    consequence_severity: Severity
    automated_seconds: float
    simulated_human_seconds: float
    simulated_manual_seconds: float
    ttr_seconds: float
