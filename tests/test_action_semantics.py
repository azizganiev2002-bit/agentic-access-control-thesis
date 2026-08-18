from access_control_experiment.evaluation import actions_equivalent
from access_control_experiment.models import Action, ActionType


def test_disable_account_target_is_not_semantically_significant():
    a = Action(type=ActionType.DISABLE_ACCOUNT, target="u401")
    b = Action(type=ActionType.DISABLE_ACCOUNT, target=None)
    assert actions_equivalent(a, b)


def test_role_removal_target_is_semantically_significant():
    a = Action(type=ActionType.REMOVE_TEMP_ACCESS, target="temp_finance")
    b = Action(type=ActionType.REMOVE_TEMP_ACCESS, target="employee_basic")
    assert not actions_equivalent(a, b)
