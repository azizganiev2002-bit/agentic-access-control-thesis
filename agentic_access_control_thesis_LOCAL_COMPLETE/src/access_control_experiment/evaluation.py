from __future__ import annotations

from copy import deepcopy
from .environment import SyntheticEnvironment
from .models import Action, Case, Severity


def expected_state(case: Case) -> dict:
    env = SyntheticEnvironment(case)
    env.apply(case.ground_truth.expected_action)
    return env.snapshot()


def state_is_correct(case: Case, actual: dict) -> bool:
    return actual == expected_state(case)


def action_is_inappropriate(case: Case, action: Action | None) -> bool:
    if action is None:
        return False
    return action != case.ground_truth.expected_action and action.type.value != "NO_ACTION"


def consequence_severity(case: Case, inappropriate_action: bool) -> Severity:
    return case.ground_truth.wrong_action_severity if inappropriate_action else Severity.NONE
