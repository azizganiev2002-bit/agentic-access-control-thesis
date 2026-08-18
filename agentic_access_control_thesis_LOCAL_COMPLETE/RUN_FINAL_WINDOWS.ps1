$ErrorActionPreference = "Stop"
& .\.venv\Scripts\Activate.ps1
$env:OLLAMA_MODEL = "qwen3:4b-instruct"
ace run --backend ollama --repetitions 5
Write-Host "Final 270-run experiment finished. Do not edit the experimental code before recording the Git commit/tag." -ForegroundColor Green
