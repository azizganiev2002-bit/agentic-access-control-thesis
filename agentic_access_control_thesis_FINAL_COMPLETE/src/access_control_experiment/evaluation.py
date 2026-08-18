from __future__ import annotations

from .environment import SyntheticEnvironment
from .models import Action, ActionType, Case, Severity


ROLE_TARGET_ACTIONS = {
    ActionType.REMOVE_TEMP_ACCESS,
    ActionType.REMOVE_PROJECT_ACCESS,
    ActionType.REMOVE_PRIVILEGED_ACCESS,
    ActionType.REMOVE_SOD_ROLE,
}


def actions_equivalent(left: Action, right: Action) -> bool:
    """Compare actions by their actual effect in the synthetic environment.

    Role-removal actions require the same target role. NO_ACTION and
    DISABLE_ACCOUNT do not use a target to determine their effect.
    """
    if left.type != right.type:
        return False
    if left.type in ROLE_TARGET_ACTIONS:
        return left.target == right.target
    return True


def expected_state(case: Case) -> dict:
    env = SyntheticEnvironment(case)
    env.apply(case.ground_truth.expected_action)
    return env.snapshot()


def state_is_correct(case: Case, actual: dict) -> bool:
    return actual == expected_state(case)


def action_is_inappropriate(case: Case, action: Action | None) -> bool:
    if action is None or action.type == ActionType.NO_ACTION:
        return False
    return not actions_equivalent(action, case.ground_truth.expected_action)


def consequence_severity(case: Case, inappropriate_action: bool) -> Severity:
    return case.ground_truth.wrong_action_severity if inappropriate_action else Severity.NONE
