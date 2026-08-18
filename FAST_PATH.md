# Fast path: free local thesis experiment

This package is the complete prototype with the Ollama backend already integrated.
It does not require a paid API.

## Fastest Windows path

1. Open PowerShell in this project folder.
2. Run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\FAST_SETUP_WINDOWS.ps1
```

If the script says Ollama is not installed, run the official Ollama installer command shown by the script, then run `FAST_SETUP_WINDOWS.ps1` again.

3. After the one-case local-AI check succeeds, run the 54-run pilot:

```powershell
.\RUN_PILOT_WINDOWS.ps1
```

4. Inspect the newest `outputs/run_*_ollama/summary.json`, `results.csv`, `audit.jsonl`, and `metadata.json`.

5. If the pilot is technically sound, commit the code to GitLab, tag the frozen experiment, then run:

```powershell
.\RUN_FINAL_WINDOWS.ps1
```

This produces 18 cases x 3 autonomy conditions x 5 repetitions = 270 runs.

## What is free

The `ollama` backend calls only the local endpoint `http://localhost:11434`. No OpenAI key is needed. Do not use `--backend openai`.
