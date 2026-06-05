#!/usr/bin/env python3
"""Batch analysis wrapper — delegates to ``core.cli.run_batch_cli``."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.cli import main

if __name__ == "__main__":
    main()
