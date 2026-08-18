from access_control_experiment.validation import validate_detector


def test_detector_validation_is_perfect():
    metrics = validate_detector()
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["fp"] == 0
    assert metrics["fn"] == 0
