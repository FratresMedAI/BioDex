#!/usr/bin/env bash
# Install CUDA-enabled PyTorch for local NVIDIA GPUs (H100, L40S, desktop/laptop, etc.).
# Use when default torch reports: CUDA driver too old / GPU available: False
# Usage: source .venv/bin/activate && bash scripts/setup_gpu.sh
set -euo pipefail

pip install -U pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124 --force-reinstall

python -c "
import torch
print('torch', torch.__version__)
print('cuda', torch.cuda.is_available())
if torch.cuda.is_available():
    print('device', torch.cuda.get_device_name(0))
"
