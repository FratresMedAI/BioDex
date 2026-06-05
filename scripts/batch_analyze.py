#!/usr/bin/env python3
"""Backward-compatible wrapper — prefer ``biodex batch``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.cli import run_batch_cli


def main() -> int:
    parser = argparse.ArgumentParser(description="BioDex batch analysis (legacy wrapper)")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("-t", "--threshold", type=float, default=0.25)
    parser.add_argument("--classify-species", action="store_true")
    parser.add_argument("-r", "--recursive", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    return run_batch_cli(
        args.input_dir,
        args.output,
        threshold=args.threshold,
        classify_species=args.classify_species,
        recursive=args.recursive,
        workers=1,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    raise SystemExit(main())
