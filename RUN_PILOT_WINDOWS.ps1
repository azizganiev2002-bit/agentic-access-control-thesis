$ErrorActionPreference = "Stop"
& .\.venv\Scripts\Activate.ps1
$env:OLLAMA_MODEL = "qwen3:4b-instruct"
ace run --backend ollama --repetitions 1
Write-Host "Pilot finished. Open the newest outputs\\run_*_ollama folder." -ForegroundColor Green
