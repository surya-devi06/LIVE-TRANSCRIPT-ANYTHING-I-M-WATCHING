# PowerShell script to launch Live Transcript in development mode
# Usage: powershell -ExecutionPolicy Bypass -File scripts\run_dev.ps1

$venvPython = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
$appScript = Join-Path $PSScriptRoot "..\app.py"

if (-not (Test-Path $venvPython)) {
    Write-Host "Virtual environment not detected. Running setup_dev.ps1 first..." -ForegroundColor Yellow
    & (Join-Path $PSScriptRoot "setup_dev.ps1")
}

Write-Host "Starting Live Transcript Desktop Application..." -ForegroundColor Cyan
& $venvPython $appScript
