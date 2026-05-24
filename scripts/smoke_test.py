#!/usr/bin/env python3
"""
Full local smoke test — requires MegaDetector (+ optional SpeciesNet) model weights.

Usage:
    python scripts/smoke_test.py
    python scripts/smoke_test.py --species
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PIL import Image

from core.detector import run_analysis
from core.exports import detections_to_csv, export_json
from core.visualization import draw_detections


def main() -> int:
    parser = argparse.ArgumentParser(description="BioDex local smoke test")
    parser.add_argument(
        "--species",
        action="store_true",
        help="Enable SpeciesNet classification (slower, downloads weights on first run)",
    )
    parser.add_argument(
        "--image",
        default=str(ROOT / "examples" / "sample.jpg"),
        help="Path to a test camera trap image",
    )
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"ERROR: image not found: {image_path}")
        return 1

    print(f"Analyzing {image_path} (species={args.species})...")
    result = run_analysis(
        Image.open(image_path),
        threshold=0.25,
        classify_species=args.species,
        filename=image_path.name,
    )
    print(result.summary)
    print(f"Detections: {result.total}")

    annotated = draw_detections(Image.open(image_path), result.detections)
    csv_path = detections_to_csv(result)
    json_path = export_json(result)
    print(f"CSV:  {csv_path}")
    print(f"JSON: {json_path}")
    print(f"Annotated size: {annotated.size}")

    if args.species and result.animal_count:
        species = next(
            (d.species for d in result.detections if d.species),
            None,
        )
        print(f"Top species: {species.label if species else 'none'}")

    print("Smoke test PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
