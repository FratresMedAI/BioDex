#!/usr/bin/env python3
"""
Volume batch demo on real LILA Channel Islands camera-trap images.

Downloads a curated subset (multi-animal frames + blanks), runs full batch
inference, and prints aggregate stats suitable for LinkedIn screenshots.

Usage:
    python -m scripts.demo_batch --species
    python scripts/demo_batch.py --max-images 60 --species
"""

from __future__ import annotations

import argparse
import io
import json
import random
import sys
import urllib.request
import zipfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.batch import run_batch
from core.types import BatchResult

from scripts import batch_smoke

DATASET_NAME = "Channel Islands Camera Traps (LILA)"
METADATA_ZIP_URL = (
    "https://storage.googleapis.com/public-datasets-lila/"
    "channel-islands-camera-traps/channel-islands-camera-traps.json.zip"
)
IMAGE_BASE_URL = (
    "https://storage.googleapis.com/public-datasets-lila/"
    "channel-islands-camera-traps/images"
)
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "biodex" / "channel-islands-demo"
DEFAULT_OUTPUT_DIR = batch_smoke.DEFAULT_OUTPUT_DIR.parent / "biodex-volume-demo"
MANIFEST_NAME = "volume_manifest.json"
EMPTY_CATEGORY_NAMES = frozenset({"empty", "blank"})


def _coco_list(metadata: dict[str, object], key: str) -> list[dict[str, Any]]:
    return cast(list[dict[str, Any]], metadata[key])


def fetch_channel_islands_metadata() -> dict[str, object]:
    """Download and parse the Channel Islands COCO metadata archive."""
    print(f"Fetching LILA metadata from {METADATA_ZIP_URL} …")
    raw = urllib.request.urlopen(METADATA_ZIP_URL, timeout=120).read()
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        inner_name = archive.namelist()[0]
        payload = archive.read(inner_name)
    metadata = json.loads(payload)
    if not isinstance(metadata, dict):
        raise ValueError("Unexpected metadata format from LILA")
    return metadata


def select_demo_filenames(
    metadata: dict[str, object],
    *,
    max_images: int,
    multi_animal_quota: int,
    blank_quota: int,
    single_animal_quota: int,
    seed: int,
) -> list[str]:
    """
    Choose a mix of dense multi-animal frames, singles, and blanks.

    Ground-truth bbox counts from LILA annotations guide selection; MegaDetector
    counts at inference time may differ slightly.
    """
    categories = {
        category["id"]: str(category["name"])
        for category in _coco_list(metadata, "categories")
    }
    empty_ids = {
        category_id
        for category_id, name in categories.items()
        if name in EMPTY_CATEGORY_NAMES
    }

    animal_counts: Counter[object] = Counter()
    for annotation in _coco_list(metadata, "annotations"):
        category_id = annotation["category_id"]
        if category_id not in empty_ids:
            animal_counts[annotation["image_id"]] += 1

    id_to_file = {
        image["id"]: str(image["file_name"])
        for image in _coco_list(metadata, "images")
    }

    multi_ids = [image_id for image_id, count in animal_counts.items() if count >= 2]
    single_ids = [image_id for image_id, count in animal_counts.items() if count == 1]
    empty_ids_list = [
        image_id for image_id in id_to_file if animal_counts.get(image_id, 0) == 0
    ]

    rng = random.Random(seed)
    selected: list[str] = []

    multi_ranked = sorted(
        multi_ids,
        key=lambda image_id: animal_counts[image_id],
        reverse=True,
    )
    dense_take = min(15, multi_animal_quota, len(multi_ranked))
    for image_id in multi_ranked[:dense_take]:
        selected.append(id_to_file[image_id])

    multi_pool = [
        id_to_file[image_id]
        for image_id in multi_ranked[dense_take:]
        if id_to_file[image_id] not in selected
    ]
    remaining_multi = multi_animal_quota - len(selected)
    if remaining_multi > 0 and multi_pool:
        selected.extend(rng.sample(multi_pool, min(remaining_multi, len(multi_pool))))

    single_pool = [id_to_file[image_id] for image_id in single_ids]
    if single_animal_quota > 0 and single_pool:
        selected.extend(
            rng.sample(single_pool, min(single_animal_quota, len(single_pool)))
        )

    blank_pool = [id_to_file[image_id] for image_id in empty_ids_list]
    if blank_quota > 0 and blank_pool:
        selected.extend(rng.sample(blank_pool, min(blank_quota, len(blank_pool))))

    unique = list(dict.fromkeys(selected))
    return unique[:max_images]


def _download_one(url: str, destination: Path) -> tuple[str, str]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.is_file() and destination.stat().st_size > 0:
        return destination.name, "skipped"
    try:
        urllib.request.urlretrieve(url, destination)
    except Exception:
        if destination.is_file():
            destination.unlink(missing_ok=True)
        return destination.name, "failed"
    return destination.name, "downloaded"


def download_demo_images(filenames: list[str], cache_dir: Path, workers: int) -> Path:
    """Download selected images into ``cache_dir`` and write a manifest."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    tasks: list[tuple[str, Path]] = []
    for filename in filenames:
        safe_name = filename.replace("/", "__")
        destination = cache_dir / safe_name
        url = f"{IMAGE_BASE_URL}/{filename}"
        tasks.append((url, destination))

    print(f"Downloading {len(tasks)} images to {cache_dir} …")
    downloaded = 0
    skipped = 0
    failed = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(_download_one, url, path): path for url, path in tasks
        }
        for future in as_completed(futures):
            _, status = future.result()
            if status == "downloaded":
                downloaded += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1

    successful = downloaded + skipped
    if failed:
        print(f"WARNING: {failed} image(s) unavailable at LILA (404 or network error).")

    manifest = {
        "dataset": DATASET_NAME,
        "source": METADATA_ZIP_URL,
        "image_base": IMAGE_BASE_URL,
        "files": [path.name for _, path in tasks if path.is_file()],
        "original_paths": filenames,
        "download_stats": {
            "requested": len(tasks),
            "downloaded": downloaded,
            "skipped": skipped,
            "failed": failed,
            "successful": successful,
        },
    }
    (cache_dir / MANIFEST_NAME).write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    print(f"Download complete: {downloaded} new, {skipped} cached, {failed} failed.")
    return cache_dir


def ensure_volume_images(
    cache_dir: Path,
    *,
    max_images: int,
    multi_animal_quota: int,
    blank_quota: int,
    single_animal_quota: int,
    seed: int,
    workers: int,
    refresh: bool,
) -> Path:
    """Ensure the cached volume demo folder contains the curated image set."""
    manifest_path = cache_dir / MANIFEST_NAME
    if not refresh and manifest_path.is_file():
        cached_count = len(batch_smoke.discover_images(cache_dir))
        if cached_count >= max(10, max_images - 5):
            print(f"Using cached volume demo images in {cache_dir} ({cached_count} files)")
            return cache_dir

    metadata = fetch_channel_islands_metadata()
    filenames = select_demo_filenames(
        metadata,
        max_images=max_images + 15,
        multi_animal_quota=multi_animal_quota + 10,
        blank_quota=blank_quota + 3,
        single_animal_quota=single_animal_quota + 2,
        seed=seed,
    )
    download_demo_images(filenames, cache_dir, workers)

    cached_count = len(batch_smoke.discover_images(cache_dir))
    if cached_count < 10:
        raise RuntimeError(
            f"Too few demo images downloaded ({cached_count}). Check LILA connectivity."
        )
    if cached_count < max_images - 5:
        print(
            f"WARNING: requested {max_images} images but only {cached_count} "
            "are available after download."
        )
    return cache_dir


def format_volume_summary(
    batch: BatchResult,
    *,
    dataset: str,
    image_dir: Path,
    csv_path: str,
    json_path: str,
    zip_path: str | None,
    show_species: bool,
) -> str:
    """Aggregate report tuned for volume / LinkedIn screenshots."""
    multi_animal_images = sum(1 for result in batch.results if result.animal_count >= 2)
    blank_rate = (batch.blank_count / batch.total_images * 100) if batch.total_images else 0.0

    lines = [
        "=== BioDex Volume Batch Demo ===",
        f"Dataset: {dataset}",
        f"Image folder: {image_dir}",
        f"Images processed: {batch.total_images}",
        f"Blanks: {batch.blank_count} ({blank_rate:.1f}%) | Failed: {len(batch.failed)}",
        f"Total detections: {batch.total_detections}",
        (
            f"Animals: {batch.animal_count} | People: {batch.person_count} "
            f"| Vehicles: {batch.vehicle_count}"
        ),
        f"Images with 2+ animals detected: {multi_animal_images}",
    ]
    if show_species and batch.species_counts:
        top_species = sorted(
            batch.species_counts.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:8]
        lines.append(f"Species counts: {dict(batch.species_counts)}")
        lines.append(
            "Top species: "
            + ", ".join(f"{name} ({count})" for name, count in top_species)
        )

    preview = batch.results[:12]
    per_image = ", ".join(
        f"{result.filename} -> {result.animal_count}" for result in preview
    )
    if len(batch.results) > len(preview):
        per_image += f", … (+{len(batch.results) - len(preview)} more)"
    lines.append(f"Per-image (sample): {per_image}")
    lines.append(f"Master CSV:  {csv_path}")
    lines.append(f"Master JSON: {json_path}")
    lines.append(f"Annotated ZIP: {zip_path or '(none)'}")
    lines.append("=== END ===")
    return "\n".join(lines)


def run_volume_demo(
    *,
    cache_dir: Path,
    output_dir: Path,
    threshold: float,
    classify_species: bool,
    max_images: int,
    multi_animal_quota: int,
    blank_quota: int,
    single_animal_quota: int,
    min_animals: int,
    min_multi_animal_images: int,
    seed: int,
    workers: int,
    refresh: bool,
) -> int:
    """Download LILA subset and run batch inference with volume validation."""
    try:
        image_dir = ensure_volume_images(
            cache_dir,
            max_images=max_images,
            multi_animal_quota=multi_animal_quota,
            blank_quota=blank_quota,
            single_animal_quota=single_animal_quota,
            seed=seed,
            workers=workers,
            refresh=refresh,
        )
    except Exception as exc:
        print(f"ERROR preparing volume demo images: {exc}")
        return 1

    images = batch_smoke.load_example_images(image_dir)
    if len(images) > max_images:
        images = images[:max_images]
    print(
        f"Volume batch: {len(images)} images from {image_dir} "
        f"(species={classify_species}, threshold={threshold})"
    )

    batch = run_batch(
        images,
        threshold=threshold,
        classify_species=classify_species,
    )

    csv_path, json_path, zip_path = batch_smoke.export_batch_artifacts(
        batch,
        images,
        output_dir,
    )
    print(
        format_volume_summary(
            batch,
            dataset=DATASET_NAME,
            image_dir=image_dir,
            csv_path=csv_path,
            json_path=json_path,
            zip_path=zip_path,
            show_species=classify_species,
        )
    )

    multi_animal_images = sum(1 for result in batch.results if result.animal_count >= 2)

    if batch.failed:
        print(f"ERROR: {len(batch.failed)} image(s) failed")
        return 1
    if batch.total_images < 10:
        print(f"ERROR: only {batch.total_images} images processed")
        return 1
    if batch.animal_count < min_animals:
        print(f"ERROR: animal_count {batch.animal_count} < min_animals {min_animals}")
        return 1
    if multi_animal_images < min_multi_animal_images:
        print(
            "ERROR: "
            f"multi-animal images {multi_animal_images} "
            f"< min_multi_animal_images {min_multi_animal_images}"
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

    print("Volume batch demo PASSED")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="BioDex volume batch demo on LILA Channel Islands camera traps",
    )
    parser.add_argument(
        "--species",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable SpeciesNet classification (default: on)",
    )
    parser.add_argument(
        "--cache-dir",
        default=str(DEFAULT_CACHE_DIR),
        help="Folder for downloaded LILA demo images",
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
        "--max-images",
        type=int,
        default=60,
        help="Maximum images to download and process",
    )
    parser.add_argument(
        "--multi-animal-quota",
        type=int,
        default=40,
        help="Target count of LILA frames with 2+ ground-truth animals",
    )
    parser.add_argument(
        "--blank-quota",
        type=int,
        default=12,
        help="Target count of blank LILA frames",
    )
    parser.add_argument(
        "--single-animal-quota",
        type=int,
        default=8,
        help="Target count of single-animal LILA frames",
    )
    parser.add_argument(
        "--min-animals",
        type=int,
        default=25,
        help="Minimum total animals required to pass",
    )
    parser.add_argument(
        "--min-multi-animal-images",
        type=int,
        default=5,
        help="Minimum images with 2+ detected animals required to pass",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible LILA subset selection",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Parallel download workers",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Re-download metadata and images even if cached",
    )
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Download LILA demo images only (no inference)",
    )
    args = parser.parse_args()

    if args.prepare_only:
        ensure_volume_images(
            Path(args.cache_dir),
            max_images=args.max_images,
            multi_animal_quota=args.multi_animal_quota,
            blank_quota=args.blank_quota,
            single_animal_quota=args.single_animal_quota,
            seed=args.seed,
            workers=args.workers,
            refresh=args.refresh,
        )
        print(f"LILA volume images ready in {args.cache_dir}")
        return 0

    return run_volume_demo(
        cache_dir=Path(args.cache_dir),
        output_dir=Path(args.output_dir),
        threshold=args.threshold,
        classify_species=args.species,
        max_images=args.max_images,
        multi_animal_quota=args.multi_animal_quota,
        blank_quota=args.blank_quota,
        single_animal_quota=args.single_animal_quota,
        min_animals=args.min_animals,
        min_multi_animal_images=args.min_multi_animal_images,
        seed=args.seed,
        workers=args.workers,
        refresh=args.refresh,
    )


if __name__ == "__main__":
    raise SystemExit(main())
