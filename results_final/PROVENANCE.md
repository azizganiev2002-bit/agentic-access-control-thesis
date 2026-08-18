\# Final Experiment Provenance



Final experimental dataset for the thesis:



\*\*Autonomy Levels in Agentic AI for Continuous Access-Control Enforcement\*\*



\## Experimental configuration



\- Code tag: `thesis-experiment-v1`

\- Code commit: `PASTE\_FULL\_COMMIT\_HASH\_HERE`

\- Backend: Ollama

\- Model: `qwen3:4b-instruct`

\- Environment: synthetic SaaS access-control environment

\- Scenario cases: 18

\- Autonomy configurations: 3

\- Repetitions per case/configuration: 5

\- Total experimental runs: 270

\- Experiment date: 18 August 2026



\## Autonomy configurations



\- A1: Detection-only

\- A2: Human-approved remediation

\- A3: Bounded autonomous remediation



\## Result files



\- `results.csv` — run-level experimental results

\- `summary.json` — aggregate metrics by autonomy configuration

\- `audit.jsonl` — detailed audit record for all runs

\- `metadata.json` — experimental configuration and model information



The `mock\_error\_rate` value present in the experiment configuration applies only

to the mock debugging backend and was not used by the final Ollama experiment.



PASTE\_FULL\_COMMIT\_HASH\_HERE: 91b820509be9ea8b69ab76602f7ebc30488d12a9

