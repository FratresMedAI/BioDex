#!/usr/bin/env python3
"""
LinkedIn-ready batch demo: aggregate stats + master CSV/JSON/annotated ZIP.

Usage:
    python scripts/batch_smoke.py --species
    python scripts/batch_smoke.py --output-dir /tmp/biodex-batch-demo --min-animals 3
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.batch import run_batch
from core.exports import batch_to_csv, build_batch_annotated_zip, export_batch_json
from core.types import BatchResult
from PIL import Image

EXAMPLES_DIR = ROOT / "examples"
DEFAULT_OUTPUT_DIR = Path(tempfile.gettempdir()) / "biodex-batch-demo"
BATCH_ANNOTATED_ZIP_LIMIT = 50
IMAGE_GLOBS = ("*.jpg", "*.jpeg", "*.png")


def discover_images(folder: Path) -> list[Path]:
    """Return sorted image paths under ``folder``."""
    paths: list[Path] = []
    for pattern in IMAGE_GLOBS:
        paths.extend(folder.glob(pattern))
    return sorted(paths)


def ensure_examples() -> int:
    """Fetch demo images when the examples folder has none."""
    if discover_images(EXAMPLES_DIR):
        return 0
    script = ROOT / "scripts" / "fetch_examples.py"
    print(f"No images in {EXAMPLES_DIR}; running {script.name} …")
    return subprocess.call([sys.executable, str(script)])


def load_example_images(folder: Path) -> list[tuple[str, Image.Image]]:
    """Load all JPG/PNG images from ``folder`` as (filename, PIL.Image) pairs."""
    paths = discover_images(folder)
    if not paths:
        raise FileNotFoundError(
            f"No images found in {folder}. Run: python scripts/fetch_examples.py"
        )
    return [(path.name, Image.open(path).convert("RGB")) for path in paths]


def export_batch_artifacts(
    batch: BatchResult,
    images: list[tuple[str, Image.Image]],
    output_dir: Path,
) -> tuple[str, str, str | None]:
    """
    Export master CSV, JSON, and annotated ZIP into ``output_dir``.

    Returns:
        Tuple of absolute paths (csv, json, zip_or_none).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    temp_csv = batch_to_csv(batch)
    temp_json = export_batch_json(batch)
    temp_zip = build_batch_annotated_zip(
        batch,
        images,
        max_images=BATCH_ANNOTATED_ZIP_LIMIT,
    )

    csv_dest = str(output_dir / "batch_summary.csv")
    json_dest = str(output_dir / "batch_summary.json")
    shutil.move(temp_csv, csv_dest)
    shutil.move(temp_json, json_dest)

    zip_dest: str | None = None
    if temp_zip:
        zip_dest = str(output_dir / "batch_annotated.zip")
        shutil.move(temp_zip, zip_dest)

    return csv_dest, json_dest, zip_dest


def format_batch_demo_summary(
    batch: BatchResult,
    csv_path: str,
    json_path: str,
    zip_path: str | None,
    *,
    show_species: bool,
) -> str:
    """Build the fixed-format summary block for screenshots."""
    lines = [
        "=== BioDex Batch Demo Summary ===",
        f"Images processed: {batch.total_images}",
        f"Blanks: {batch.blank_count} | Failed: {len(batch.failed)}",
        f"Total detections: {batch.total_detections}",
        (
            f"Animals: {batch.animal_count} | People: {batch.person_count} "
            f"| Vehicles: {batch.vehicle_count}"
        ),
    ]
    if show_species and batch.species_counts:
        lines.append(f"Species counts: {batch.species_counts}")
    per_image = ", ".join(
        f"{result.filename} -> {result.animal_count}"
        for result in batch.results
    )
    lines.append(f"Per-image: {per_image}")
    lines.append(f"Master CSV:  {csv_path}")
    lines.append(f"Master JSON: {json_path}")
    lines.append(f"Annotated ZIP: {zip_path or '(none)'}")
    lines.append("=== END ===")
    return "\n".join(lines)


def run_batch_demo(
    *,
    examples_dir: Path,
    output_dir: Path,
    threshold: float,
    classify_species: bool,
    min_animals: int,
) -> int:
    """
    Run batch analysis on example images and export demo artifacts.

    Returns:
        0 on success, non-zero if validation fails.
    """
    if examples_dir == EXAMPLES_DIR:
        if not discover_images(examples_dir) and ensure_examples() != 0:
            return 1
    elif not discover_images(examples_dir):
        print(f"ERROR: no images found in {examples_dir}")
        return 1

    images = load_example_images(examples_dir)
    print(f"Batch demo: {len(images)} images from {examples_dir} (species={classify_species})")

    batch = run_batch(
        images,
        threshold=threshold,
        classify_species=classify_species,
    )

    csv_path, json_path, zip_path = export_batch_artifacts(batch, images, output_dir)
    print(format_batch_demo_summary(
        batch,
        csv_path,
        json_path,
        zip_path,
        show_species=classify_species,
    ))

    if batch.failed:
        print(f"ERROR: {len(batch.failed)} image(s) failed")
        return 1
    if batch.animal_count < min_animals:
        print(
            f"ERROR: animal_count {batch.animal_count} < min_animals {min_animals}"
        )
        return 1
    if not Path(csv_path).is_file() or Path(csv_path).stat().st_size == 0:
        print(f"ERROR: master CSV missing or empty: {csv_path}")
        return 1
    if not Path(json_path).is_file() or Path(json_path).stat().st_size == 0:
        print(f"ERROR: master JSON missing or empty: {json_path}")
        return 1
    if zip_path and (not Path(zip_path).is_file() or Path(zip_path).stat().st_size == 0):
        print(f"ERROR: annotated ZIP missing or empty: {zip_path}")
        return 1

    print("Batch demo PASSED")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="BioDex LinkedIn batch demo")
    parser.add_argument(
        "--species",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable SpeciesNet classification (default: on)",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for master CSV, JSON, and annotated ZIP",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.25,
        help="MegaDetector confidence threshold",
    )
    parser.add_argument(
        "--min-animals",
        type=int,
        default=3,
        help="Minimum total animals required to pass",
    )
    parser.add_argument(
        "--examples-dir",
        default=str(EXAMPLES_DIR),
        help="Folder of demo images (default: examples/)",
    )
    args = parser.parse_args()

    return run_batch_demo(
        examples_dir=Path(args.examples_dir),
        output_dir=Path(args.output_dir),
        threshold=args.threshold,
        classify_species=args.species,
        min_animals=args.min_animals,
    )


if __name__ == "__main__":
    raise SystemExit(main())
