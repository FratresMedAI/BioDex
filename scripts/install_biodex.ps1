# Reproducible BioDex install on Windows (protobuf-safe megadetector + speciesnet).
# Usage: .\scripts\install_biodex.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "Step 1/5: Creating virtual environment" -ForegroundColor Cyan
python -m venv .venv
& .\.venv\Scripts\Activate.ps1

python -m pip install -U pip wheel

Write-Host "Step 2/5: protobuf pin (megadetector/yolov5 requirement)" -ForegroundColor Cyan
pip install "protobuf==3.20.1"

Write-Host "Step 3/5: MegaDetector (must be >=10.0, not PyPI 5.x)" -ForegroundColor Cyan
pip install "megadetector>=10.0,<11.0"

Write-Host "Step 4/5: UI + numerics (CPU torch)" -ForegroundColor Cyan
pip install "torch>=2.0" "Pillow>=9.5" "numpy>=1.26.4,<2.0" "pandas>=2.1" "tqdm>=4.64" "setuptools>=65.0,<81.0"

Write-Host "Step 5/5: SpeciesNet + editable package" -ForegroundColor Cyan
pip install "speciesnet>=5.0,<6.0"
if ($LASTEXITCODE -ne 0) {
    pip install "speciesnet>=5.0,<6.0" --no-deps
}
pip install -e ".[ui,dev]"
pip install "protobuf==3.20.1" --force-reinstall -q

python -c "import megadetector; import speciesnet; print('BioDex install OK')"
Write-Host ""
Write-Host "=== BioDex install complete ===" -ForegroundColor Green
Write-Host "Activate: .\.venv\Scripts\Activate.ps1"
Write-Host "Desktop build: .\scripts\build_desktop.ps1"
Write-Host "CLI: biodex batch <folder> -o <output>"
