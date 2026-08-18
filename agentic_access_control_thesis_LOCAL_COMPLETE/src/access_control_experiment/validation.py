from __future__ import annotations

from .detector import RuleEngine
from .loader import load_detector_validation, load_experiment_config


def validate_detector() -> dict[str, float | int]:
    cfg = load_experiment_config()
    detector = RuleEngine(cfg["as_of_date"])
    cases = load_detector_validation()
    tp = fp = tn = fn = 0
    for case in cases:
        predicted = detector.detect(case).triggered
        expected = case.ground_truth.detector_should_trigger
        if predicted and expected:
            tp += 1
        elif predicted and not expected:
            fp += 1
        elif not predicted and not expected:
            tn += 1
        else:
            fn += 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "precision": precision, "recall": recall}
