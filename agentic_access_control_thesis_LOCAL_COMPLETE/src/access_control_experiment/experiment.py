from __future__ import annotations

import csv
import json
import time
import uuid
from pathlib import Path
from statistics import median
from typing import Any

from .detector import RuleEngine
from .environment import SyntheticEnvironment
from .evaluation import action_is_inappropriate, consequence_severity, state_is_correct
from .guardrails import GuardrailEngine
from .human_review import SimulatedHumanReviewer
from .loader import load_actions, load_cases, load_experiment_config, load_policies
from .models import Action, AgentDecision, Case, RunRecord, Severity
from .reasoners import MockReasoner, OllamaReasoner, OpenAIReasoner, Reasoner
from .tools import AgentTools


class ExperimentRunner:
    def __init__(self, backend: str, repetitions: int | None = None, mock_error_rate: float | None = None):
        self.config = load_experiment_config()
        self.cases = load_cases()
        self.policies = load_policies()
        self.actions = load_actions()
        self.detector = RuleEngine(self.config["as_of_date"])
        self.guardrails = GuardrailEngine(self.actions)
        self.human = SimulatedHumanReviewer()
        self.repetitions = repetitions or int(self.config["repetitions"])
        self.backend = backend
        self.reasoner = self._make_reasoner(backend, mock_error_rate)

    def _make_reasoner(self, backend: str, mock_error_rate: float | None) -> Reasoner:
        if backend == "mock":
            rate = self.config["mock_error_rate"] if mock_error_rate is None else mock_error_rate
            return MockReasoner(error_rate=float(rate), seed=int(self.config["random_seed"]))
        if backend == "openai":
            return OpenAIReasoner()
        if backend == "ollama":
            return OllamaReasoner()
        raise ValueError("backend must be 'mock', 'ollama', or 'openai'")

    def run_all(self) -> list[RunRecord]:
        records: list[RunRecord] = []
        for rep in range(1, self.repetitions + 1):
            for case in self.cases:
                for autonomy in ("A1", "A2", "A3"):
                    records.append(self.run_one(case, autonomy, rep))
        return records

    def run_one(self, case: Case, autonomy: str, repetition: int) -> RunRecord:
        env = SyntheticEnvironment(case)
        detection = self.detector.detect(case)
        if not detection.triggered:
            raise RuntimeError(f"Experimental case {case.case_id} did not trigger its detector")

        context = AgentTools.gather_context(case, env, detection)
        automated_start = time.perf_counter()
        agent_decision: AgentDecision | None = None
        guardrail = None
        human_intervention = False
        human_decision = None
        executed_action: Action | None = None
        executed_by: str | None = None
        human_seconds = 0.0
        manual_seconds = 0.0

        if autonomy == "A1":
            human_intervention = True
            executed_action, human_decision = self.human.decide(case)
            env.apply(executed_action)
            executed_by = "human"
            human_seconds += float(self.config["human_review_delay_seconds"])
            if executed_action.type.value != "NO_ACTION":
                manual_seconds += float(self.config["manual_remediation_delay_seconds"])

        elif autonomy == "A2":
            agent_decision = self.reasoner.recommend(case, self.policies[case.policy_id], context)
            human_intervention = True
            executed_action, human_decision = self.human.decide(case, agent_decision)
            env.apply(executed_action)
            executed_by = "agent_after_human_approval" if agent_decision.action == executed_action else "human_corrected"
            human_seconds += float(self.config["human_review_delay_seconds"])
            if executed_by == "human_corrected" and executed_action.type.value != "NO_ACTION":
                manual_seconds += float(self.config["manual_remediation_delay_seconds"])

        elif autonomy == "A3":
            agent_decision = self.reasoner.recommend(case, self.policies[case.policy_id], context)
            guardrail = self.guardrails.evaluate(
                case.policy_id,
                agent_decision,
                env,
                context_complete=case.agent_context_complete,
            )
            if guardrail.autonomous_allowed:
                executed_action = agent_decision.action
                env.apply(executed_action)
                executed_by = "agent_autonomous"
            else:
                human_intervention = True
                executed_action, human_decision = self.human.decide(case, agent_decision)
                env.apply(executed_action)
                executed_by = "human_after_escalation"
                human_seconds += float(self.config["human_review_delay_seconds"])
                if executed_action.type.value != "NO_ACTION":
                    manual_seconds += float(self.config["manual_remediation_delay_seconds"])
        else:
            raise ValueError(f"Unknown autonomy configuration: {autonomy}")

        automated_seconds = time.perf_counter() - automated_start
        final_correct = state_is_correct(case, env.snapshot())
        inappropriate = action_is_inappropriate(case, executed_action if executed_by == "agent_autonomous" else None)
        severity = consequence_severity(case, inappropriate)
        remediation_success = final_correct if case.ground_truth.is_violation else None
        ttr = automated_seconds + human_seconds + manual_seconds

        return RunRecord(
            run_id=str(uuid.uuid4()),
            case_id=case.case_id,
            scenario_family=case.scenario_family,
            variant=case.variant,
            policy_id=case.policy_id,
            autonomy=autonomy,
            repetition=repetition,
            backend=self.backend,
            detector_triggered=detection.triggered,
            agent_action=agent_decision.action.type.value if agent_decision else None,
            agent_target=agent_decision.action.target if agent_decision else None,
            agent_rationale=agent_decision.rationale if agent_decision else None,
            guardrail_allowed=guardrail.autonomous_allowed if guardrail else None,
            guardrail_reasons=guardrail.reasons if guardrail else [],
            human_intervention=human_intervention,
            human_decision=human_decision,
            executed_action=executed_action.type.value if executed_action else None,
            executed_target=executed_action.target if executed_action else None,
            executed_by=executed_by,
            inappropriate_action_executed=inappropriate,
            final_state_correct=final_correct,
            remediation_success=remediation_success,
            consequence_severity=severity,
            automated_seconds=automated_seconds,
            simulated_human_seconds=human_seconds,
            simulated_manual_seconds=manual_seconds,
            ttr_seconds=ttr,
        )


def write_outputs(records: list[RunRecord], output_dir: Path, metadata: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fields = list(RunRecord.model_fields.keys())
    with (output_dir / "results.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in records:
            row = r.model_dump(mode="json")
            row["guardrail_reasons"] = json.dumps(row["guardrail_reasons"])
            writer.writerow(row)

    with (output_dir / "audit.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            f.write(r.model_dump_json() + "\n")

    summary = summarize(records)
    with (output_dir / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    with (output_dir / "metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


def summarize(records: list[RunRecord]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for autonomy in ("A1", "A2", "A3"):
        rs = [r for r in records if r.autonomy == autonomy]
        genuine = [r for r in rs if r.remediation_success is not None]
        incorrect = [r for r in rs if r.inappropriate_action_executed]
        severities: dict[str, int] = {}
        for r in incorrect:
            severities[r.consequence_severity.value] = severities.get(r.consequence_severity.value, 0) + 1
        result[autonomy] = {
            "runs": len(rs),
            "median_ttr_seconds": median([r.ttr_seconds for r in rs]) if rs else None,
            "RSR": sum(bool(r.remediation_success) for r in genuine) / len(genuine) if genuine else None,
            "HIR": sum(r.human_intervention for r in rs) / len(rs) if rs else None,
            "IRR": sum(r.inappropriate_action_executed for r in rs) / len(rs) if rs else None,
            "CS_distribution": severities,
        }
    return result
