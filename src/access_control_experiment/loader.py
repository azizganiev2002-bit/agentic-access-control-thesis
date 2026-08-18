from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import yaml

from .models import Case


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_cases(path: Path | None = None) -> list[Case]:
    path = path or PROJECT_ROOT / "data" / "cases.json"
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return [Case.model_validate(item) for item in data]


def load_detector_validation(path: Path | None = None) -> list[Case]:
    path = path or PROJECT_ROOT / "data" / "detector_validation.json"
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return [Case.model_validate(item) for item in data]


def load_policies() -> dict[str, Any]:
    return load_yaml(PROJECT_ROOT / "config" / "policies.yaml")["policies"]


def load_actions() -> dict[str, Any]:
    return load_yaml(PROJECT_ROOT / "config" / "actions.yaml")["actions"]


def load_experiment_config() -> dict[str, Any]:
    return load_yaml(PROJECT_ROOT / "config" / "experiment.yaml")
