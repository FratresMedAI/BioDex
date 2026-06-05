#!/usr/bin/env bash
# Run the limited public demo locally (same restrictions as Hugging Face).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  echo "Installing BioDex first..."
  bash scripts/install_biodex.sh
fi

# shellcheck disable=SC1091
source .venv/bin/activate
export BIODEX_DEPLOY=1
cd demo
echo "Limited demo → http://127.0.0.1:7860 (max 30 images, no ZIP)"
exec python app.py
