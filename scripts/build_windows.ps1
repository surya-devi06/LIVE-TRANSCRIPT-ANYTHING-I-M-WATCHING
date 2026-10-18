<#
.SYNOPSIS
    Build a standalone Windows executable for Live Transcript v0.1.0 using PyInstaller.

.DESCRIPTION
    1. Verifies the virtual environment exists.
    2. Runs pytest (44 tests) to confirm the source is healthy before building.
    3. Runs PyInstaller with live_transcript.spec (onedir, no console, icon embedded).
    4. Reports the size of the output dist\LiveTranscript\ directory.
    5. Lists the generated executable and key DLLs so you can spot obvious omissions.

.USAGE
    From the project root:
        .\scripts\build_windows.ps1

    To skip tests and go straight to build:
        .\scripts\build_windows.ps1 -SkipTests
#>

param(
    [switch]$SkipTests
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Venv        = Join-Path $ProjectRoot ".venv"
$Python      = Join-Path $Venv "Scripts\python.exe"
$PyInstaller = Join-Path $Venv "Scripts\pyinstaller.exe"
$SpecFile    = Join-Path $ProjectRoot "live_transcript.spec"
$DistDir     = Join-Path $ProjectRoot "dist\LiveTranscript"
$Exe         = Join-Path $DistDir "LiveTranscript.exe"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Live Transcript — Windows Build Script" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ── 1. Verify venv ────────────────────────────────────────────────────────────
if (-not (Test-Path $Python)) {
    Write-Error "Virtual environment not found at $Venv. Run: python -m venv .venv && .\.venv\Scripts\pip install -r requirements.txt"
    exit 1
}
Write-Host "[1/5] Virtual environment: OK ($Python)" -ForegroundColor Green

# ── 2. Verify PyInstaller ─────────────────────────────────────────────────────
if (-not (Test-Path $PyInstaller)) {
    Write-Host "[2/5] PyInstaller not found. Installing..." -ForegroundColor Yellow
    & $Python -m pip install pyinstaller --quiet
}
$ver = & $PyInstaller --version 2>&1
Write-Host "[2/5] PyInstaller: $ver" -ForegroundColor Green

# ── 3. Run tests ──────────────────────────────────────────────────────────────
if (-not $SkipTests) {
    Write-Host ""
    Write-Host "[3/5] Running test suite..." -ForegroundColor Cyan
    & $Python -m pytest tests/ -q --tb=short
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Tests failed (exit $LASTEXITCODE). Fix failures before building."
        exit 1
    }
    Write-Host "[3/5] All tests passed." -ForegroundColor Green
} else {
    Write-Host "[3/5] Tests skipped (-SkipTests flag)." -ForegroundColor Yellow
}

# ── 4. Run PyInstaller ────────────────────────────────────────────────────────
Write-Host ""
Write-Host "[4/5] Building with PyInstaller..." -ForegroundColor Cyan
Write-Host "      Spec: $SpecFile"
Write-Host "      Output: $DistDir"
Write-Host ""

Set-Location $ProjectRoot
& $PyInstaller $SpecFile --clean --noconfirm

if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller failed (exit $LASTEXITCODE). Check output above."
    exit 1
}

# ── 5. Report ─────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "[5/5] Build complete." -ForegroundColor Green

if (Test-Path $Exe) {
    $ExeSize = (Get-Item $Exe).Length / 1MB
    Write-Host "  Executable : $Exe" -ForegroundColor White
    Write-Host ("  Exe size   : {0:N1} MB" -f $ExeSize) -ForegroundColor White
} else {
    Write-Warning "Executable not found at expected path: $Exe"
}

# Total dist folder size
$TotalBytes = (Get-ChildItem $DistDir -Recurse | Measure-Object -Property Length -Sum).Sum
$TotalMB    = [Math]::Round($TotalBytes / 1MB, 1)
Write-Host ("  Total dist : {0} MB" -f $TotalMB) -ForegroundColor White
Write-Host "  Dist path  : $DistDir" -ForegroundColor White

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Key files in dist\LiveTranscript\" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Get-ChildItem $DistDir | Where-Object { $_.Extension -in ".exe",".dll",".pyd" -or $_.PSIsContainer } | Sort-Object Name | Format-Table Name, @{L="Size(MB)";E={"{0:N2}" -f ($_.Length/1MB)}} -AutoSize

Write-Host ""
Write-Host "To verify the build:" -ForegroundColor Yellow
Write-Host '  & "dist\LiveTranscript\LiveTranscript.exe"' -ForegroundColor White
Write-Host ""
