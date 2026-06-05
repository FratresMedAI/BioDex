# Build BioDex desktop app on Windows (.exe in dist\BioDex\).
# Requires: scripts/install_biodex.ps1 equivalent or manual venv + pip install pyinstaller
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: .venv not found. Run .\scripts\install_biodex.ps1 first." -ForegroundColor Red
    exit 1
}

& .\.venv\Scripts\Activate.ps1
pip install -q pyinstaller

Write-Host "Building BioDex desktop bundle (several minutes, large output)..." -ForegroundColor Cyan
pyinstaller packaging\biodex-desktop.spec --noconfirm

Write-Host ""
Write-Host "=== Desktop build complete ===" -ForegroundColor Green
Write-Host "Run: dist\BioDex\BioDex.exe"
Write-Host "Zip dist\BioDex for distribution, or wrap with Inno Setup for a single installer."
