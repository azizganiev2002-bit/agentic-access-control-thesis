# Runbook: from code to final thesis experiment

This is the practical sequence to follow after downloading the project.

## Phase 1 — Get the project running locally

### Windows

1. Install Python 3.11+ and Git.
2. Extract the project ZIP.
3. Open PowerShell inside the extracted folder.
4. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

5. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

6. Run tests:

```powershell
pytest -q
```

7. Validate the fixed detector:

```powershell
ace validate-detector
```

8. Smoke-test the whole pipeline:

```powershell
ace run --backend mock --repetitions 1 --mock-error-rate 0
```

Open the new `outputs/run_..._mock/` directory and inspect `results.csv`, `summary.json`, and `audit.jsonl`.

## Phase 2 — Review the synthetic experiment before collecting results

Do not immediately run the final experiment. First review:

- `config/policies.yaml` — make sure every policy is defensible.
- `config/actions.yaml` — make sure low/high impact assignments match Chapter 4.
- `data/cases.json` — inspect all 18 cases and their ground truth.
- `config/experiment.yaml` — freeze the human-review and manual-remediation delay assumptions.

If you change any of these, update Chapter 4 before collecting final data.

## Phase 3 — Put the implementation in GitLab

Create a blank GitLab project. Then in PowerShell, from the project directory:

```powershell
git init
git add .
git commit -m "Initial thesis prototype"
git branch -M main
git remote add origin https://gitlab.com/YOUR_USERNAME/agentic-access-control-thesis.git
git push -u origin main
```

After every meaningful change:

```powershell
git status
git add .
git commit -m "Describe the change"
git push
```

Never commit `.env` or an API key.

## Phase 4 — Freeze the experimental implementation

When tests pass and the 18 cases are final:

```powershell
git add .
git commit -m "Freeze implementation for thesis experiment"
git push
git tag -a thesis-experiment-v1 -m "Final implementation used for thesis experiment"
git push origin thesis-experiment-v1
git rev-parse HEAD
```

Copy the commit hash somewhere safe. It will be referenced in the thesis.

## Phase 5 — Run the real agent

Set the API credentials only in your shell environment:

```powershell
$env:OPENAI_API_KEY="YOUR_API_KEY"
$env:OPENAI_MODEL="gpt-5.6"
```

Run one real pilot first:

```powershell
ace run --backend openai --repetitions 1
```

Inspect the audit log. Confirm that agent recommendations contain no obvious schema or prompt problems. If you change the prompt after this pilot, commit the change and create a new tag before final collection.

Run the final experiment only after the implementation is frozen:

```powershell
ace run --backend openai --repetitions 5
```

This should generate 270 run records.

## Phase 6 — Preserve the final results

Rename the final output directory to something explicit, for example:

```text
outputs/final_openai_gpt56_20260818/
```

Do not overwrite it. Copy it as a backup.

If the data contain no secrets and you want the final result dataset in GitLab, force-add only the final directory because `outputs/` is ignored by default:

```powershell
git add -f outputs/final_openai_gpt56_20260818/results.csv
git add -f outputs/final_openai_gpt56_20260818/summary.json
git add -f outputs/final_openai_gpt56_20260818/metadata.json
git commit -m "Add final thesis experiment results"
git push
```

You may leave `audit.jsonl` out of the public repository if it is large; keep it in your local/archive copy and appendix materials as appropriate.

## Phase 7 — Write Chapters 5 and 6

Chapter 5 should describe what is actually implemented, especially:

- Python and configuration files;
- synthetic environment and case schema;
- deterministic rule engine;
- bounded context tools;
- LLM reasoner and structured output;
- A1/A2/A3 controller;
- simulated human reviewer;
- A3 guardrails;
- audit logging and metric pipeline;
- reproducibility through Git commit/tag and stored experiment configuration.

Chapter 6 should be produced from the frozen `results.csv` and `summary.json`, not from memory or manually typed numbers.

## Phase 8 — Repository reference in the thesis

Once you know your actual GitLab URL and final commit hash, use wording similar to:

> The prototype implementation and synthetic experimental configuration are maintained in the accompanying GitLab repository at \texttt{<repository URL>}. The results reported in this thesis were generated using release \texttt{thesis-experiment-v1}, commit \texttt{<commit hash>}. The repository contains the policy definitions, synthetic cases, deterministic detector, post-detection agent, autonomy controller, guardrails, simulated reviewer, and experimental runner.

If the repository is private, replace “available” with wording such as “made available to the supervisor and examiners.”
