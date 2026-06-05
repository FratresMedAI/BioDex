#!/usr/bin/env python3
"""
Download example camera trap images for BioDex demos.

Usage:
    python scripts/fetch_examples.py
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "examples"
MANIFEST_PATH = EXAMPLES_DIR / "manifest.json"

SAMPLE_URLS = {
    "sample.jpg": (
        "https://github.com/agentmorris/MegaDetector/raw/main/images/orinoquia-thumb-web.jpg"
    ),
}


def _download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {destination.name}...")
    urllib.request.urlretrieve(url, destination)
    print(f"Saved {destination}")


def main() -> int:
    if not MANIFEST_PATH.exists():
        print(f"ERROR: manifest not found at {MANIFEST_PATH}")
        return 1

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    samples = manifest.get("samples", [])
    if not samples:
        print("No samples listed in manifest.")
        return 1

    for sample in samples:
        filename = sample.get("file")
        if not filename:
            continue
        destination = EXAMPLES_DIR / filename
        if destination.exists():
            print(f"Already present: {destination}")
            continue
        url = SAMPLE_URLS.get(filename)
        if not url:
            print(f"WARNING: no download URL configured for {filename}")
            continue
        try:
            _download(url, destination)
        except Exception as exc:
            print(f"ERROR downloading {filename}: {exc}")
            return 1

    print("Example images ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
