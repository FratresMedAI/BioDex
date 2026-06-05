#!/usr/bin/env bash
# Build BioDex desktop app (folder bundle with BioDex executable).
# Requires: bash scripts/install_biodex.sh && pip install pyinstaller
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
source .venv/bin/activate

pip install -q pyinstaller

echo "Building BioDex desktop bundle (this can take several minutes)..."
pyinstaller packaging/biodex-desktop.spec --noconfirm

if [[ "$(uname -s)" == "Darwin" ]]; then
  echo ""
  echo "=== Desktop build complete ==="
  echo "App: dist/BioDex.app"
  echo "Zip for sharing: ditto -c -k --sequesterRsrc dist/BioDex.app dist/BioDex-mac.zip"
else
  echo ""
  echo "=== Desktop build complete ==="
  echo "Run: dist/BioDex/BioDex"
  echo "Zip the dist/BioDex folder for distribution."
fi
