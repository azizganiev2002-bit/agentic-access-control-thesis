from access_control_experiment.detector import RuleEngine
from access_control_experiment.environment import SyntheticEnvironment
from access_control_experiment.guardrails import GuardrailEngine
from access_control_experiment.loader import load_actions, load_cases, load_experiment_config
from access_control_experiment.models import Action, ActionType, AgentDecision


def _case(case_id):
    return next(c for c in load_cases() if c.case_id == case_id)


def test_low_impact_clear_case_can_be_autonomous():
    c = _case("S1-CLEAR")
    env = SyntheticEnvironment(c)
    g = GuardrailEngine(load_actions())
    d = AgentDecision(action=Action(type=ActionType.REMOVE_TEMP_ACCESS, target="temp_finance"), rationale="test")
    out = g.evaluate(c.policy_id, d, env, True)
    assert out.autonomous_allowed


def test_valid_exception_forces_review():
    c = _case("S1-EXCEPTION")
    env = SyntheticEnvironment(c)
    g = GuardrailEngine(load_actions())
    d = AgentDecision(action=Action(type=ActionType.NO_ACTION), rationale="test")
    out = g.evaluate(c.policy_id, d, env, True)
    assert not out.autonomous_allowed
    assert "valid_exception" in out.reasons


def test_high_impact_action_forces_review():
    c = _case("S4-CLEAR")
    env = SyntheticEnvironment(c)
    g = GuardrailEngine(load_actions())
    d = AgentDecision(action=Action(type=ActionType.DISABLE_ACCOUNT), rationale="test")
    out = g.evaluate(c.policy_id, d, env, True)
    assert not out.autonomous_allowed
    assert "high_impact_action" in out.reasons
