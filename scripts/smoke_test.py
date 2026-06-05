#!/usr/bin/env python3
"""
Full local smoke test — requires MegaDetector (+ optional SpeciesNet) model weights.

Usage:
    python scripts/smoke_test.py
    python scripts/smoke_test.py --species
    python scripts/smoke_test.py --batch examples/
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.detector import analyze_single_image
from core.exports import (
    detections_to_csv,
    export_bundle,
    export_json,
)
from core.visualization import draw_detections
from PIL import Image

from scripts import batch_smoke


def _analyze_one(image_path: Path, species: bool) -> int:
    result = analyze_single_image(
        Image.open(image_path),
        threshold=0.25,
        classify_species=species,
        filename=image_path.name,
    )
    print(result.summary)
    print(f"Detections: {result.total}")
    if result.warnings:
        print("Warnings:", "; ".join(result.warnings))

    annotated = draw_detections(Image.open(image_path), result.detections)
    csv_path = detections_to_csv(result)
    json_path = export_json(result)
    bundle_path = export_bundle(result, annotated)
    print(f"CSV:    {csv_path}")
    print(f"JSON:   {json_path}")
    print(f"Bundle: {bundle_path}")
    print(f"Annotated size: {annotated.size}")

    if species and result.animal_count:
        top = next((d.species for d in result.detections if d.species), None)
        print(f"Top species: {top.label if top else 'none'}")
    return 0


def _analyze_batch(folder: Path, species: bool) -> int:
    return batch_smoke.run_batch_demo(
        examples_dir=folder,
        output_dir=batch_smoke.DEFAULT_OUTPUT_DIR,
        threshold=0.25,
        classify_species=species,
        min_animals=1,
    )


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
    parser.add_argument(
        "--batch",
        default="",
        help="Folder of images for batch smoke test",
    )
    args = parser.parse_args()

    if args.batch:
        folder = Path(args.batch)
        if not folder.is_dir():
            print(f"ERROR: batch folder not found: {folder}")
            return 1
        print(f"Batch analyzing {folder} (species={args.species})...")
        code = _analyze_batch(folder, args.species)
    else:
        image_path = Path(args.image)
        if not image_path.exists():
            examples_dir = ROOT / "examples"
            example_images = sorted(
                [
                    *examples_dir.glob("*.jpg"),
                    *examples_dir.glob("*.jpeg"),
                    *examples_dir.glob("*.png"),
                ]
            )
            if example_images:
                print(
                    f"WARNING: default image missing ({image_path}). "
                    f"Using {example_images[0]}"
                )
                image_path = example_images[0]
            else:
                print(f"ERROR: image not found: {image_path}")
                print("Run: python scripts/fetch_examples.py")
                return 1
        print(f"Analyzing {image_path} (species={args.species})...")
        code = _analyze_one(image_path, args.species)

    if code == 0:
        print("Smoke test PASSED")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
