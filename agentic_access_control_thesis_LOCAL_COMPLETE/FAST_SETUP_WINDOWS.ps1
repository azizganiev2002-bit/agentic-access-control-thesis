$ErrorActionPreference = "Stop"

Write-Host "=== Thesis prototype: FREE LOCAL setup ===" -ForegroundColor Cyan

# 1. Python project setup
if (-not (Test-Path ".venv")) {
    Write-Host "Creating Python virtual environment..."
    python -m venv .venv
}

& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"

Write-Host "Running tests..."
pytest -q
Write-Host "Validating deterministic detector..."
ace validate-detector

# 2. Locate Ollama without relying on PATH
$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
$ollamaExe = $null
if ($ollamaCmd) {
    $ollamaExe = $ollamaCmd.Source
}

if (-not $ollamaExe) {
    $candidate = Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"
    if (Test-Path $candidate) { $ollamaExe = $candidate }
}

if (-not $ollamaExe) {
    $candidate = Join-Path $HOME "Downloads\ollama.exe"
    if (Test-Path $candidate) { $ollamaExe = $candidate }
}

if (-not $ollamaExe) {
    Write-Host "" 
    Write-Host "Ollama is not installed/found." -ForegroundColor Yellow
    Write-Host "Fast official install command:" -ForegroundColor Yellow
    Write-Host 'irm https://ollama.com/install.ps1 | iex' -ForegroundColor White
    Write-Host "Run that command in PowerShell, then re-run this script." -ForegroundColor Yellow
    exit 1
}

Write-Host "Using Ollama: $ollamaExe"

# Try to ensure the app/API is available. Installed Windows Ollama normally runs in background.
try {
    Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 3 | Out-Null
} catch {
    Write-Host "Starting Ollama server..."
    Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 4
}

# 3. Pull a local model (no paid API)
$model = "qwen3:4b-instruct"
$env:OLLAMA_MODEL = $model
Write-Host "Pulling local model $model (first run downloads about 2.5 GB)..."
& $ollamaExe pull $model

# 4. Small real local-AI check
Write-Host "Running one local-AI case..."
ace run-one --backend ollama --case-id S1-CLEAR --autonomy A3

Write-Host ""
Write-Host "SETUP COMPLETE." -ForegroundColor Green
Write-Host "Next command for the 54-run pilot:" -ForegroundColor Green
Write-Host 'ace run --backend ollama --repetitions 1'
