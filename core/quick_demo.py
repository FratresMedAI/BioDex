"""
Curated frame selection for the UI Quick demo (screenshots / LinkedIn).

Selects frames by MegaDetector animal counts (1–5 animals), not LILA metadata.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from PIL import Image

logger = logging.getLogger(__name__)

QUICK_DEMO_COUNT = 10
QUICK_DEMO_MIN_ANIMALS = 1
QUICK_DEMO_MAX_ANIMALS = 5
MANIFEST_NAME = "quick_demo_manifest.json"
MANIFEST_VERSION = 2
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def _list_cached_images(cache_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in cache_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )


def _manifest_path(cache_dir: Path) -> Path:
    return cache_dir / MANIFEST_NAME


def _load_manifest(cache_dir: Path) -> list[str] | None:
    path = _manifest_path(cache_dir)
    if not path.is_file():
        return None
    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return None
        if (
            isinstance(payload, dict)
            and payload.get("version") == MANIFEST_VERSION
            and isinstance(payload.get("frames"), list)
        ):
            return [str(name) for name in payload["frames"]]
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not read quick-demo manifest: %s", exc)
    return None


def _save_manifest(cache_dir: Path, filenames: list[str]) -> None:
    _manifest_path(cache_dir).write_text(
        json.dumps({"version": MANIFEST_VERSION, "frames": filenames}, indent=2),
        encoding="utf-8",
    )


def _paths_from_manifest(cache_dir: Path, filenames: list[str]) -> list[Path]:
    paths: list[Path] = []
    for name in filenames:
        path = cache_dir / name
        if path.is_file():
            paths.append(path)
    return paths


def scan_quick_demo_paths(
    cache_dir: Path,
    *,
    count: int = QUICK_DEMO_COUNT,
    min_animals: int = QUICK_DEMO_MIN_ANIMALS,
    max_animals: int = QUICK_DEMO_MAX_ANIMALS,
    threshold: float = 0.25,
) -> list[Path]:
    """
    Scan the cache with MegaDetector and return frames with 1–max_animals detections.

    Blanks (0 animals) and dense multi-animal frames are excluded.
    """
    from core.detector import run_detection, warmup_models

    warmup_models(species=False)
    picked: list[Path] = []

    for path in _list_cached_images(cache_dir):
        try:
            with Image.open(path) as handle:
                image = handle.convert("RGB")
            result = run_detection(image, threshold=threshold)
        except Exception as exc:
            logger.warning("Quick demo scan skipped %s: %s", path.name, exc)
            continue

        if min_animals <= result.animal_count <= max_animals:
            picked.append(path)
            logger.info(
                "Quick demo pick %s -> %s animals",
                path.name,
                result.animal_count,
            )
        if len(picked) >= count:
            break

    return picked


def ensure_quick_demo_paths(
    cache_dir: Path,
    *,
    count: int = QUICK_DEMO_COUNT,
    min_animals: int = QUICK_DEMO_MIN_ANIMALS,
    max_animals: int = QUICK_DEMO_MAX_ANIMALS,
    threshold: float = 0.25,
    refresh: bool = False,
) -> list[Path]:
    """
    Return exactly ``count`` frames with 1–max_animals MegaDetector animals.

    Reuses a cached manifest when valid; rescans when missing or ``refresh=True``.
    """
    if not refresh:
        manifest = _load_manifest(cache_dir)
        if manifest:
            paths = _paths_from_manifest(cache_dir, manifest)
            if len(paths) >= count:
                return paths[:count]

    picked = scan_quick_demo_paths(
        cache_dir,
        count=count,
        min_animals=min_animals,
        max_animals=max_animals,
        threshold=threshold,
    )
    if picked:
        _save_manifest(cache_dir, [path.name for path in picked])
    return picked[:count]


__all__ = [
    "QUICK_DEMO_COUNT",
    "QUICK_DEMO_MAX_ANIMALS",
    "QUICK_DEMO_MIN_ANIMALS",
    "ensure_quick_demo_paths",
    "scan_quick_demo_paths",
]
