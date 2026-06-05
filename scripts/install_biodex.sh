#!/usr/bin/env bash
# Reproducible BioDex install (avoids megadetector/speciesnet protobuf ResolutionImpossible).
# Usage: bash scripts/install_biodex.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

pip install -U pip wheel

echo "Step 1/5: protobuf pin (megadetector/yolov5 requirement)"
pip install "protobuf==3.20.1"

echo "Step 2/5: MegaDetector (must be >=10.0, not PyPI 5.x)"
pip install "megadetector>=10.0,<11.0"

echo "Step 3/5: UI + numerics (CPU torch; run setup_gpu.sh for H100/CUDA)"
pip install "torch>=2.0" "Pillow>=9.5" "numpy>=1.26.4,<2.0" "pandas>=2.1" "tqdm>=4.64" "setuptools>=65.0,<81.0"

echo "Step 4/5: SpeciesNet (may warn on protobuf; runtime OK with pin above)"
pip install "speciesnet>=5.0,<6.0" || pip install "speciesnet>=5.0,<6.0" --no-deps

echo "Step 5/5: editable package (CLI + UI extras) + dev tools"
pip install -e ".[ui,dev]"

pip install "protobuf==3.20.1" --force-reinstall -q

python -c "import megadetector; import speciesnet; print('BioDex install OK')"
