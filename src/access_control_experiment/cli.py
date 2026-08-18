from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .experiment import ExperimentRunner, write_outputs
from .loader import load_experiment_config
from .validation import validate_detector


def main() -> None:
    parser = argparse.ArgumentParser(prog="ace", description="Agentic access-control autonomy experiment")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate-detector", help="Validate the deterministic detector on positive and negative controls")

    run = sub.add_parser("run", help="Run the A1/A2/A3 experiment")
    run.add_argument("--backend", choices=["mock", "openai"], default="mock")
    run.add_argument("--repetitions", type=int, default=None)
    run.add_argument("--mock-error-rate", type=float, default=None)
    run.add_argument("--output-dir", type=Path, default=None)

    args = parser.parse_args()

    if args.command == "validate-detector":
        print(json.dumps(validate_detector(), indent=2))
        return

    if args.command == "run":
        runner = ExperimentRunner(args.backend, args.repetitions, args.mock_error_rate)
        records = runner.run_all()
        if args.output_dir is None:
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path("outputs") / f"run_{stamp}_{args.backend}"
        else:
            output_dir = args.output_dir
        cfg = load_experiment_config()
        metadata = {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "backend": args.backend,
            "repetitions": runner.repetitions,
            "experiment_config": cfg,
        }
        write_outputs(records, output_dir, metadata)
        print(f"Wrote {len(records)} run records to {output_dir}")
        print(json.dumps(json.loads((output_dir / "summary.json").read_text()), indent=2))
