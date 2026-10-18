# PowerShell Development Environment Setup for Windows 11
# Usage: powershell -ExecutionPolicy Bypass -File scripts\setup_dev.ps1

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Live Transcript - Development Environment Setup" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Locate Python 3.10
$pythonCmd = "python"
if (Get-Command "py" -ErrorAction SilentlyContinue) {
    $pythonCmd = "py -3.10"
}

Write-Host "`n[1/4] Checking Python environment ($pythonCmd)..." -ForegroundColor Yellow
& $pythonCmd --version
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python 3.10 is required but was not found. Please install Python 3.10 64-bit."
    exit 1
}

# Create virtual environment if missing
$venvPath = Join-Path $PSScriptRoot "..\.venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "`n[2/4] Creating virtual environment at .venv..." -ForegroundColor Yellow
    & $pythonCmd -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment."
        exit 1
    }
} else {
    Write-Host "`n[2/4] Virtual environment already exists at .venv." -ForegroundColor Green
}

# Activate virtual environment
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    Write-Error "Activate.ps1 script not found at $activateScript"
    exit 1
}

Write-Host "`n[3/4] Activating virtual environment..." -ForegroundColor Yellow
. $activateScript

$venvPython = Join-Path $venvPath "Scripts\python.exe"

# Upgrade pip & install requirements
Write-Host "`n[4/4] Installing core dependencies from requirements.txt..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip
$reqFile = Join-Path $PSScriptRoot "..\requirements.txt"
& $venvPython -m pip install -r $reqFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n==========================================================" -ForegroundColor Green
    Write-Host " Setup Complete! You can now run the application:" -ForegroundColor Green
    Write-Host "   powershell -File scripts\run_dev.ps1" -ForegroundColor White
    Write-Host " Or run tests with:" -ForegroundColor White
    Write-Host "   .venv\Scripts\python.exe -m pytest tests/unit -v" -ForegroundColor White
    Write-Host "==========================================================" -ForegroundColor Green
} else {
    Write-Error "Dependency installation encountered errors."
    exit 1
}
