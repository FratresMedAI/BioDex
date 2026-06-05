#!/usr/bin/env bash
# Full RunPod setup: install, GPU torch, static checks, live smoke test.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

bash scripts/install_biodex.sh
bash scripts/setup_gpu.sh

source .venv/bin/activate
python scripts/fetch_examples.py

echo "=== VOLUME BATCH DEMO (GPU) ==="
python -m scripts.demo_batch --species

echo "=== RUFF ==="
ruff check . --output-format=concise

echo "=== MYPY ==="
mypy . --strict 2>&1 | head -80

echo "=== PYTEST FAST ==="
pytest tests/ -v -m "not slow" --tb=short

echo "=== SMOKE SPECIES (GPU) ==="
python scripts/test_mega_load.py
python scripts/smoke_test.py --species

echo "=== RUNPOD SETUP COMPLETE ==="
