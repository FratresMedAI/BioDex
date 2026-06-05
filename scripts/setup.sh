#!/usr/bin/env bash
# BioDex environment setup — Linux / macOS / WSL
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> BioDex setup in $ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found. Use Python 3.10–3.12."
  exit 1
fi

PYVER="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
case "$PYVER" in
  3.10|3.11|3.12) ;;
  *)
    echo "ERROR: Python $PYVER is unsupported. Use 3.10–3.12."
    exit 1
    ;;
esac

python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

pip install --upgrade pip wheel "setuptools>=65,<81"

# CUDA torch first on GPU hosts (optional)
if command -v nvidia-smi >/dev/null 2>&1; then
  echo "==> NVIDIA GPU detected — installing CUDA PyTorch"
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
fi

pip install -r requirements.txt

echo "==> Fetching demo sample image"
python scripts/fetch_examples.py

echo "==> Verifying Gradio app builds"
python -c "from app import build_app; build_app(); print('app build OK')"

echo ""
echo "Setup complete. Next steps:"
echo "  source .venv/bin/activate"
echo "  python scripts/smoke_test.py"
echo "  python scripts/smoke_test.py --species"
echo "  BIODEX_HOST=0.0.0.0 python app.py"
