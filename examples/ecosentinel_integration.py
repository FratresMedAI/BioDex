#!/usr/bin/env python3
"""EcoSentinel integration example.

Runs a BioDex batch over a folder of camera-trap images and emits the
EcoSentinel sensor-fusion JSON payload, then shows how a downstream
EcoSentinel ingestion step would consume it.

The ``export_ecosentinel`` schema is a versioned stub
(``ecosentinel/0.5-stub``); full drone/acoustic sensor fusion lives in the
Fratres EcoSentinel stack. This example demonstrates the stable hand-off
contract so integrators can build against it today.

Usage:
    python examples/ecosentinel_integration.py path/to/images --out payload.json
    python examples/ecosentinel_integration.py path/to/images --classify-species

Requires the model extras to run real inference:
    pip install -e ".[models]"
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from core.batch import run_batch_from_paths
from core.exports import export_ecosentinel
from core.types import BatchResult

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def _collect_images(folder: Path, recursive: bool) -> list[tuple[str, str]]:
    """Return (filename, absolute_path) pairs for images under ``folder``."""
    walker = folder.rglob("*") if recursive else folder.glob("*")
    pairs = [
        (p.name, str(p.resolve()))
        for p in sorted(walker)
        if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES
    ]
    if not pairs:
        raise SystemExit(f"No images ({', '.join(sorted(IMAGE_SUFFIXES))}) found in {folder}")
    return pairs


def run_biodex_batch(folder: Path, *, classify_species: bool, recursive: bool) -> BatchResult:
    """Detect (and optionally classify) every image in ``folder``."""
    path_pairs = _collect_images(folder, recursive)
    print(f"Analyzing {len(path_pairs)} image(s) from {folder} ...")
    return run_batch_from_paths(
        path_pairs,
        threshold=0.25,
        classify_species=classify_species,
    )


def ingest_into_ecosentinel(payload: dict) -> None:
    """Stand-in for the EcoSentinel ingestion API.

    Replace this with a real POST to your EcoSentinel endpoint, e.g.:

        import httpx
        httpx.post(f"{ECO_BASE_URL}/v0/observations",
                   headers={"Authorization": f"Bearer {token}"},
                   json=payload, timeout=30).raise_for_status()
    """
    summary = payload["summary"]
    print("\n--- EcoSentinel ingestion (simulated) ---")
    print(f"schema_version : {payload['schema_version']}")
    print(f"source         : {payload['source']} v{payload['biodex_version']}")
    print(f"total_images   : {payload['total_images']}")
    print(f"animals        : {summary['animals']}")
    print(f"fusion_ready   : {payload['fusion_ready']}")
    top = sorted(summary["species_counts"].items(), key=lambda kv: kv[1], reverse=True)[:5]
    if top:
        print("top species    : " + ", ".join(f"{name} ({n})" for name, n in top))
    print(f"observations   : {len(payload['observations'])} records ready for fusion")


def main() -> None:
    parser = argparse.ArgumentParser(description="BioDex -> EcoSentinel integration example")
    parser.add_argument("folder", type=Path, help="Folder of camera-trap images")
    parser.add_argument("--out", type=Path, default=None, help="Where to save the payload JSON")
    parser.add_argument(
        "--classify-species",
        action="store_true",
        help="Run SpeciesNet on animal detections (needs the [models] extra)",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Do not descend into subfolders",
    )
    args = parser.parse_args()

    batch = run_biodex_batch(
        args.folder,
        classify_species=args.classify_species,
        recursive=not args.no_recursive,
    )

    # export_ecosentinel writes to a temp file and returns its path.
    tmp_path = Path(export_ecosentinel(batch))
    payload = json.loads(tmp_path.read_text(encoding="utf-8"))

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmp_path), str(args.out))
        print(f"Wrote EcoSentinel payload -> {args.out}")
    else:
        tmp_path.unlink(missing_ok=True)

    ingest_into_ecosentinel(payload)


if __name__ == "__main__":
    main()
