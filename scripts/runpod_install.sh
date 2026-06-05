#!/usr/bin/env bash
set -euo pipefail
cd /workspace/BioDex
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel "setuptools>=65,<81"
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
pip install -r requirements.txt
python scripts/fetch_examples.py
python -c "from app import build_app; build_app(); print('app OK')"
pip install pytest
pytest tests/ -q
python scripts/smoke_test.py
echo "=== RUNPOD INSTALL COMPLETE ==="
