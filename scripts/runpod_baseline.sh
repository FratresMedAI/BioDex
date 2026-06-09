#!/usr/bin/env bash
set -x
LOG=/tmp/biodex-baseline.log
exec > "$LOG" 2>&1

pkill -f "pip install|app.py|runpod_diagnostics" 2>/dev/null || true
rm -rf ~/BioDex && git clone https://github.com/Fratres-X-Natura/BioDex.git && cd ~/BioDex

python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install "protobuf==3.20.1"
pip install "megadetector>=10.0,<11.0"
pip install "gradio>=5,<7" torch Pillow "numpy<2" pandas tqdm
pip install "speciesnet>=5.0,<6.0"
pip install -r requirements-ci-core.txt

echo "=== IMPORT CHECK ==="
python -c "import megadetector; import speciesnet; print('imports ok')"

echo "=== RUFF ==="
ruff check . --output-format=concise

echo "=== MYPY (first 100 lines) ==="
mypy . --strict 2>&1 | head -100

echo "=== SMOKE TEST SPECIES ==="
python scripts/smoke_test.py --species

echo "=== BASELINE COMPLETE ==="
