#!/usr/bin/env bash
set -x
exec > /tmp/biodex-diagnostics.log 2>&1

cd ~ && rm -rf BioDex || true
git clone https://github.com/FratresMedAI/BioDex.git
cd BioDex

python -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-ci.txt

# Immediate conflict mitigation
pip install "protobuf>=4.21,<5.0" --force-reinstall || true

python -c "import megadetector; import speciesnet; print('imports ok')"

ruff check .
mypy . --strict 2>&1 | head -100

python -m pytest tests/ -v --tb=short 2>&1 | tail -50

python scripts/smoke_test.py 2>&1 | tail -30
python scripts/smoke_test.py --species 2>&1 | tail -30

echo "=== DIAGNOSTICS COMPLETE ==="
