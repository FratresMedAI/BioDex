#!/usr/bin/env bash
# OPTIONAL legacy helper for remote GPU dev environments — not required for local use.
# Full local install: bash scripts/install_biodex.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

bash scripts/install_biodex.sh
bash scripts/setup_gpu.sh

source .venv/bin/activate
python scripts/fetch_examples.py

echo "=== PREPARE LILA VOLUME DATA ==="
python -m scripts.demo_batch --prepare-only

echo "=== PRODUCT CLI BATCH (GPU) ==="
biodex batch "$HOME/.cache/biodex/channel-islands-demo" \
  --output /tmp/biodex-cli-batch-out \
  --classify-species \
  --recursive

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
