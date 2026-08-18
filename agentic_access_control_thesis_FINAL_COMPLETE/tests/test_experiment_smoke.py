from access_control_experiment.experiment import ExperimentRunner


def test_one_repetition_has_54_runs_and_expected_hir_pattern():
    r = ExperimentRunner("mock", repetitions=1, mock_error_rate=0.0)
    records = r.run_all()
    assert len(records) == 18 * 3
    a1 = [x for x in records if x.autonomy == "A1"]
    a2 = [x for x in records if x.autonomy == "A2"]
    a3 = [x for x in records if x.autonomy == "A3"]
    assert all(x.human_intervention for x in a1)
    assert all(x.human_intervention for x in a2)
    assert any(not x.human_intervention for x in a3)
