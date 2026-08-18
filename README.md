# Agentic Access-Control Autonomy Experiment

Research prototype for the thesis **Autonomy Levels in Agentic AI for Continuous Access-Control Enforcement**.

The project implements a controlled synthetic experiment with one deterministic access-control detector and three post-detection autonomy configurations:

- **A1 — Detection-only:** a human reviews the detected case, decides the appropriate response, and performs remediation.
- **A2 — Human-approved remediation:** the agent gathers context and recommends a remediation action, but a simulated human must approve or reject the recommendation before execution.
- **A3 — Bounded autonomous remediation:** the agent may execute only predefined low-impact remediation actions when all guardrails are satisfied; otherwise the case is escalated for human review.

The implementation is designed to isolate **post-detection autonomy**. The deterministic detection mechanism, policy definitions, synthetic cases, and ground truth remain constant across A1, A2, and A3. Only the authority granted after detection changes.

The A3 guardrails include policy/action allowlisting, valid-exception checks, action-impact gating, incomplete-context escalation, restricted tool access, and execution logging.

## 1. Requirements

- Python 3.11 or newer
- Git
- Ollama
- Local model: `qwen3:4b-instruct`

The final thesis experiment was executed locally through Ollama using `qwen3:4b-instruct`.

**No paid cloud API was used to generate the reported thesis results.**

The implementation also contains an optional OpenAI backend, but that backend was not used for the final thesis experiment.

The `mock` backend is provided only for debugging, testing, and validation of the experimental pipeline. Mock results are not used as empirical thesis results.

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

## 3. Validate the implementation

Run the automated tests:

```bash
pytest -q
```

Validate the deterministic rule engine:

```bash
ace validate-detector
```

The supplied validation dataset is designed to confirm that the fixed rule implementation corresponds to the synthetic policy definitions.

For the frozen implementation used in the experiment, the detector validation produced:

```text
Precision: 1.0
Recall:    1.0
```

This validation is separate from the autonomy experiment. The same deterministic detector is used in all three autonomy configurations.

## 4. Debugging and smoke testing

A mock reasoning backend is included to verify the complete experimental pipeline without invoking an LLM.

Run a one-repetition smoke test:

```bash
ace run --backend mock --repetitions 1 --mock-error-rate 0
```

This creates:

```text
18 cases × 3 autonomy configurations × 1 repetition = 54 runs
```

A stronger debugging test can deliberately inject recommendation errors:

```bash
ace run --backend mock --repetitions 5 --mock-error-rate 0.15
```

These commands are intended only for development and debugging.

**Mock-backend results were not used for the final thesis evaluation.**

## 5. Final thesis experiment

The final experiment reported in the thesis was executed locally using Ollama and the `qwen3:4b-instruct` model.

Install or start Ollama and ensure the model is available:

```powershell
ollama pull qwen3:4b-instruct
```

The final experiment can be reproduced with:

```powershell
ace run --backend ollama --repetitions 5
```

On Windows, the supplied helper script may alternatively be used:

```powershell
.\RUN_FINAL_WINDOWS.ps1
```

The experiment consists of:

```text
18 synthetic cases
×
3 autonomy configurations
×
5 repetitions
=
270 experimental runs
```

The same model, detector, policies, cases, tools, prompts, and experiment configuration are retained across the experiment.

The final run metadata records:

```text
Backend:       Ollama
Model:         qwen3:4b-instruct
Cases:         18
Configurations: 3
Repetitions:   5
Total runs:    270
```

### Optional OpenAI backend

The implementation also provides an optional OpenAI reasoning backend using structured outputs.

It was **not used for the final thesis results**.

If required for separate testing, it can be configured through environment variables such as:

```powershell
$env:OPENAI_API_KEY="YOUR_API_KEY"
$env:OPENAI_MODEL="YOUR_MODEL"

ace run --backend openai --repetitions 1
```

API access and billing are separate from ChatGPT subscriptions.

## 6. Experimental outputs

Each experiment creates a timestamped directory under `outputs/`, for example:

```text
outputs/run_<timestamp>_ollama/
├── results.csv
├── audit.jsonl
├── summary.json
└── metadata.json
```

The files have the following purposes:

- `results.csv` contains one record for every experimental run.
- `audit.jsonl` contains the detailed machine-readable audit trail for each run.
- `summary.json` contains aggregate metrics for A1, A2, and A3.
- `metadata.json` records the backend, model, repetition count, timestamp, and experiment configuration.

Temporary and development runs under `outputs/` are ignored by Git.

The final 270-run dataset used in the thesis is archived separately under:

```text
results_final/
├── results.csv
├── summary.json
├── metadata.json
├── audit.jsonl
├── PROVENANCE.md
└── SHA256SUMS.txt
```

`PROVENANCE.md` identifies the experiment version and configuration.

`SHA256SUMS.txt` contains SHA-256 hashes of the archived evidence files to support integrity verification.

## 7. Final experimental results

The final experiment consisted of 90 runs for each autonomy configuration, producing 270 runs in total.

| Configuration | Runs | Median TTR | RSR | HIR | IRR |
|---|---:|---:|---:|---:|---:|
| A1 — Detection-only | 90 | 20.00 s | 1.00 | 1.00 | 0.00 |
| A2 — Human-approved remediation | 90 | 18.51 s | 1.00 | 1.00 | 0.00 |
| A3 — Bounded autonomous remediation | 90 | 19.35 s | 1.00 | 0.8333 | 0.00 |

No inappropriate remediation action was executed in the final experiment. Consequently, the observed incorrect-remediation rate was zero for all three configurations and no observed action required assignment of consequence severity.

This does not imply that the agent produced no incorrect recommendations. Recommendation errors occurred during post-detection reasoning, but the human-approval mechanism in A2 and the bounded-autonomy guardrails in A3 prevented those errors from becoming inappropriate executed actions.

Detailed interpretation of the results is provided in the thesis rather than in this repository README.

## 8. Project structure

```text
agentic_access_control_thesis/
├── config/
│   ├── actions.yaml
│   ├── experiment.yaml
│   └── policies.yaml
│
├── data/
│   ├── cases.json
│   └── detector_validation.json
│
├── results_final/
│   ├── results.csv
│   ├── summary.json
│   ├── metadata.json
│   ├── audit.jsonl
│   ├── PROVENANCE.md
│   └── SHA256SUMS.txt
│
├── src/
│   └── access_control_experiment/
│       ├── detector.py
│       ├── environment.py
│       ├── tools.py
│       ├── reasoners.py
│       ├── guardrails.py
│       ├── human_review.py
│       ├── evaluation.py
│       ├── experiment.py
│       ├── validation.py
│       └── cli.py
│
├── tests/
│
├── FAST_SETUP_WINDOWS.ps1
├── RUN_PILOT_WINDOWS.ps1
├── RUN_FINAL_WINDOWS.ps1
├── FAST_PATH.md
├── RUNBOOK.md
├── THESIS_MAPPING.md
├── README.md
├── pyproject.toml
└── .gitignore
```

The most important implementation components are:

- `detector.py` — fixed deterministic policy-checking engine.
- `environment.py` — synthetic SaaS access-control environment and write operations.
- `tools.py` — bounded context-retrieval and remediation tools.
- `reasoners.py` — mock, Ollama, and optional OpenAI reasoning backends.
- `guardrails.py` — A3 bounded-autonomy authorization checks.
- `human_review.py` — deterministic simulated human reviewer.
- `evaluation.py` — comparison with ground truth and evaluation logic.
- `experiment.py` — orchestration of A1, A2, and A3 and experiment logging.
- `validation.py` — independent detector validation.
- `cli.py` — command-line interface.

## 9. Experimental cases

The experiment uses six access-control scenario families with three variants per family, producing 18 cases.

The scenario families cover:

1. expired temporary access;
2. obsolete project access;
3. inappropriate privileged access;
4. enabled accounts belonging to terminated users;
5. inactive identities requiring contextual review; and
6. segregation-of-duties conflicts.

Each family contains variants designed to represent a clear violation, a valid exception, and a contextual or boundary case.

The complete ground-truth definitions are contained in:

```text
data/cases.json
```

The experiment uses synthetic data only and does not connect to production identity or SaaS systems.

## 10. Autonomy configurations

### A1 — Detection-only

The deterministic detector identifies a potential violation.

A simulated human reviewer determines the appropriate response and performs remediation.

Every detected case therefore requires human intervention.

### A2 — Human-approved remediation

The agent gathers context and proposes a remediation action.

A simulated human reviewer must approve or reject the recommendation before execution.

This configuration preserves a mandatory human decision checkpoint for every case.

### A3 — Bounded autonomous remediation

The agent may execute a remediation without case-by-case human approval only when the applicable guardrails are satisfied.

Autonomous execution is restricted to eligible low-impact actions.

Cases involving high-impact actions, valid exceptions, incomplete context, prohibited actions, invalid targets, or other guardrail conditions are escalated for human review.

## 11. Reproducing the final experiment

The repository contains two version markers with different purposes.

### Experimental code version

The tag:

```text
thesis-experiment-v1
```

identifies the source-code version used to generate the final experiment.

To inspect that version:

```bash
git checkout thesis-experiment-v1
```

Create the environment and install dependencies:

```bash
pip install -e ".[dev]"
```

Run the tests:

```bash
pytest -q
```

Validate the detector:

```bash
ace validate-detector
```

Ensure Ollama and the model are available:

```bash
ollama pull qwen3:4b-instruct
```

The final experimental procedure can then be reproduced with:

```bash
ace run --backend ollama --repetitions 5
```

### Archived result version

The tag:

```text
thesis-results-v1
```

identifies the repository state containing the archived final 270-run dataset under `results_final/`.

The archived files can be compared with newly generated outputs when reproducing the experiment.

## 12. Version control and reproducibility

The implementation is maintained in an accompanying GitHub repository.

Two annotated Git tags are used:

- `thesis-experiment-v1` — exact implementation used to generate the final experiment.
- `thesis-results-v1` — repository state containing the final archived experimental evidence.

The exact experimental code commit can additionally be identified using:

```bash
git rev-list -n 1 thesis-experiment-v1
```

The final results archive contains both provenance information and file-integrity hashes.

No credentials, API keys, Python virtual environments, or temporary experiment outputs should be committed to the repository.

## 13. Referencing the implementation in the thesis

The full source code should not be reproduced in Chapter 5.

Instead, the chapter describes the architecture, important implementation decisions, experiment configuration, and reproducibility mechanisms.

A suitable reproducibility statement is:

> The implementation used for the experiment is preserved in the accompanying GitHub repository under the tag `thesis-experiment-v1` (commit `<commit-hash>`). The final 270-run experimental dataset, including run-level results, aggregate metrics, experiment metadata, and audit records, is archived under the tag `thesis-results-v1` in the `results_final/` directory.

If the repository remains private during assessment, access can be provided directly to the supervisor or examiners.