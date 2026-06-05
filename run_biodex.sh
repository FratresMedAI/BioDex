#!/usr/bin/env bash
# Start BioDex locally. First run installs automatically.
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
  echo "First run — installing (5–10 min). Needs Python 3.10–3.12 and internet."
  bash scripts/install_biodex.sh
fi

# shellcheck disable=SC1091
source .venv/bin/activate
echo ""
echo "BioDex → http://127.0.0.1:7860"
echo "Upload a camera-trap folder, then click Process Folder."
echo ""
exec biodex-ui
