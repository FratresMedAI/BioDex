#!/usr/bin/env bash
# Run THIS on the RunPod pod (Jupyter terminal or SSH) — survives disconnects.
set -euo pipefail
cd /workspace/BioDex
source .venv/bin/activate

echo "==> Finishing BioDex install..."
pip install -r requirements.txt
python scripts/fetch_examples.py

echo "==> Smoke test (detection only)..."
python scripts/smoke_test.py

echo "==> Smoke test (with species)..."
python scripts/smoke_test.py --species

echo "==> Starting Gradio on port 7860 (all interfaces)..."
export BIODEX_HOST=0.0.0.0
export BIODEX_PORT=7860
python app.py
