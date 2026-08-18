# Agentic Access-Control Autonomy Experiment

Research prototype for the thesis **Autonomy Levels in Agentic AI for Continuous Access-Control Enforcement**.

The project implements a controlled synthetic experiment with one deterministic detector and three post-detection autonomy configurations:

- **A1 — Detection-only:** human decides and remediates.
- **A2 — Human-approved remediation:** the agent recommends; a simulated human approves/rejects before execution.
- **A3 — Bounded autonomous remediation:** the agent may execute only when guardrails allow it; otherwise the case is escalated.

The guardrails implement the design described in the thesis: policy/action allowlisting, valid-exception checks, low-impact gating, incomplete-context escalation, and bounded tool access.

## 1. Requirements

- Python 3.11 or newer
- Git
- Optional: an OpenAI API key if you want to run the actual LLM backend

> The `mock` backend exists only for local debugging, tests, and checking the experiment pipeline. Do **not** use mock results as the final empirical results of an Agentic-AI thesis.

## 2. Installation

### Windows PowerShell

```powershell
cd path\to\agentic_access_control_thesis
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### macOS / Linux

```bash
cd path/to/agentic_access_control_thesis
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## 3. Check the code before experimenting

Run the unit tests:

```bash
pytest -q
```

Validate the deterministic rule engine on separate positive and negative controls:

```bash
ace validate-detector
```

The supplied validation set is expected to produce precision = 1.0 and recall = 1.0 because it is designed to confirm that the fixed rule implementation matches the synthetic policy definitions.

## 4. Smoke-test the complete pipeline

Run one repetition with the local mock reasoner and no injected reasoning errors:

```bash
ace run --backend mock --repetitions 1 --mock-error-rate 0
```

This should create 54 runs:

```text
18 cases × 3 autonomy configurations × 1 repetition = 54
```

For a stronger guardrail-pipeline test, allow the mock backend to inject some synthetic recommendation errors:

```bash
ace run --backend mock --repetitions 5 --mock-error-rate 0.15
```

Again, these are **debugging runs**, not final thesis results.

## 5. Run the actual LLM experiment

The optional OpenAI backend uses structured outputs so that each LLM recommendation is parsed into the same `AgentDecision` schema used by the rest of the experiment.

Set your API key and model in the environment. API access/billing is separate from a ChatGPT subscription.

### Windows PowerShell

```powershell
$env:OPENAI_API_KEY="YOUR_API_KEY"
$env:OPENAI_MODEL="gpt-5.6"
ace run --backend openai --repetitions 5
```

### macOS / Linux

```bash
export OPENAI_API_KEY="YOUR_API_KEY"
export OPENAI_MODEL="gpt-5.6"
ace run --backend openai --repetitions 5
```

You can replace the model value with another model available to your API project. For the final thesis experiment, use one fixed model and record its exact identifier in Chapter 5 and in the run metadata.

The full experiment contains:

```text
18 cases × 3 autonomy configurations × 5 repetitions = 270 runs
```

## 6. Output files

Each run creates a directory under `outputs/`, for example:

```text
outputs/run_20260818_103000_openai/
├── results.csv
├── audit.jsonl
├── summary.json
└── metadata.json
```

- `results.csv` — one row per experimental run; use this for Chapter 6 tables and charts.
- `audit.jsonl` — detailed machine-readable audit record for every run.
- `summary.json` — A1/A2/A3 aggregate TTR, RSR, HIR, IRR, and CS distribution.
- `metadata.json` — backend, repetition count, timestamps, and experiment configuration.

Outputs are ignored by Git by default so that raw generated results are not accidentally mixed with source-code commits. When you freeze the final experiment, either add the selected final result files explicitly (`git add -f ...`) or place a sanitized final dataset in a separate `results_final/` folder and commit it deliberately.

## 7. Project structure

```text
agentic_access_control_thesis/
├── config/
│   ├── actions.yaml          # allowed actions and impact class
│   ├── experiment.yaml       # repetitions and simulated human delays
│   └── policies.yaml         # six synthetic policy definitions
├── data/
│   ├── cases.json            # 18 ground-truth experiment cases
│   └── detector_validation.json
├── src/access_control_experiment/
│   ├── detector.py           # fixed deterministic rule engine
│   ├── environment.py        # synthetic SaaS state + write operations
│   ├── tools.py              # bounded context-gathering tools
│   ├── reasoners.py          # mock + OpenAI agent reasoning backends
│   ├── guardrails.py         # A3 bounded-autonomy checks
│   ├── human_review.py       # deterministic simulated reviewer
│   ├── evaluation.py         # ground-truth comparison + CS handling
│   ├── experiment.py         # A1/A2/A3 orchestration + output pipeline
│   ├── validation.py         # detector validation
│   └── cli.py                # command-line interface
├── tests/
├── .gitlab-ci.yml
└── README.md
```

## 8. GitLab workflow

Create a new blank project in GitLab, for example:

```text
agentic-access-control-thesis
```

Do not initialize it with a README if you are pushing this existing folder.

Inside the project folder run:

```bash
git init
git add .
git commit -m "Initial thesis prototype"
git branch -M main
git remote add origin https://gitlab.com/YOUR_USERNAME/agentic-access-control-thesis.git
git push -u origin main
```

If your GitLab account requires a personal access token, use that according to your GitLab authentication setup rather than committing credentials to the repository.

For later changes:

```bash
git status
git add src config data tests README.md
git commit -m "Refine autonomy guardrails and experiment cases"
git push
```

Before running the final experiment, make a tag so the exact code used for the thesis can be recovered:

```bash
git tag -a thesis-experiment-v1 -m "Code used for final thesis experiment"
git push origin thesis-experiment-v1
```

After results are finalized, record the Git commit hash:

```bash
git rev-parse HEAD
```

Use that hash in Chapter 5 or the appendix/reproducibility statement so the reader can identify the exact implementation used.

## 9. What to cite in the thesis

Do not paste the full source code into Chapter 5. Describe the architecture and include only short illustrative snippets if needed. Put the repository URL and the exact commit/tag in the implementation or reproducibility subsection, for example:

> The implementation used for the experiment is available in the accompanying GitLab repository. The results reported in Chapter 6 were generated from release `thesis-experiment-v1` (commit `<commit-hash>`). The repository contains the synthetic case definitions, deterministic detection engine, autonomy controller, guardrail logic, simulated reviewer, and experiment runner.

If the repository must remain private during assessment, state that it is available to the supervisor/examiners rather than claiming that it is publicly accessible.

## 10. Recommended thesis workflow from this point

1. Run `pytest -q` and `ace validate-detector`.
2. Run one mock smoke test and inspect `results.csv` and `audit.jsonl`.
3. Read the 18 cases in `data/cases.json` and confirm that you can justify every policy, expected action, exception, action-impact class, and CS label.
4. Push the stable code to GitLab.
5. Freeze the code with a Git tag before collecting final results.
6. Run the actual LLM experiment with one fixed model and five repetitions.
7. Save the final output directory and commit/tag the exact experiment configuration.
8. Write Chapter 5 from the implementation that actually ran.
9. Generate Chapter 6 tables/charts from `results.csv`.
10. Interpret the trade-off in Chapter 7; do not change the methodology after seeing results unless you explicitly document the change and rerun the experiment.
