#!/usr/bin/env bash
# Full verification on RunPod (H100). Usage: bash scripts/runpod_verify.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

source /root/biodex-venv/bin/activate

echo "=== Fix protobuf pin ==="
pip install "protobuf==3.20.1" --force-reinstall -q

echo "=== GPU / torch check ==="
python -c "
import torch
print('torch', torch.__version__)
print('cuda available', torch.cuda.is_available())
if torch.cuda.is_available():
    print('device', torch.cuda.get_device_name(0))
"

echo "=== Import check ==="
python -c "import megadetector; import speciesnet; print('imports ok')"

echo "=== pytest fast ==="
pytest tests/ -v -m "not slow"

echo "=== ruff ==="
ruff check core app.py

echo "=== mypy ==="
mypy core

echo "=== app build ==="
python -c "from app import build_app; build_app(); print('app ok')"

echo "=== fetch examples ==="
python scripts/fetch_examples.py

echo "=== smoke detection ==="
python scripts/smoke_test.py

echo "=== smoke species ==="
python scripts/smoke_test.py --species

echo "=== batch CLI ==="
python scripts/batch_analyze.py examples/ -o /tmp/biodex-batch-out -v

echo "=== slow test (live inference) ==="
pytest tests/test_detector.py::test_analyze_single_image_live_smoke -v

echo "=== ALL VERIFICATION PASSED ==="
