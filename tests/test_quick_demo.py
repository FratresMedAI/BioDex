"""Tests for quick-demo frame selection."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from core.quick_demo import (
    MANIFEST_VERSION,
    QUICK_DEMO_COUNT,
    ensure_quick_demo_paths,
    scan_quick_demo_paths,
)


def _make_detection(animal_count: int) -> MagicMock:
    result = MagicMock()
    result.animal_count = animal_count
    return result


def test_scan_picks_only_frames_with_one_to_five_animals(tmp_path: Path) -> None:
    names = ["blank.jpg", "one.jpg", "five.jpg", "crowd.jpg"]
    for name in names:
        (tmp_path / name).write_bytes(b"fake")

    counts = {"blank.jpg": 0, "one.jpg": 1, "five.jpg": 5, "crowd.jpg": 12}
    scan_order = sorted(names)

    with (
        patch("core.detector.warmup_models"),
        patch("core.detector.run_detection") as run_detection,
        patch("PIL.Image.open") as open_image,
    ):
        open_image.return_value.__enter__.return_value.convert.return_value = object()
        run_detection.side_effect = [
            _make_detection(counts[name]) for name in scan_order
        ]

        picked = scan_quick_demo_paths(tmp_path, count=2)

    assert [path.name for path in picked] == ["five.jpg", "one.jpg"]


def test_ensure_quick_demo_uses_manifest_when_valid(tmp_path: Path) -> None:
    for name in ("a.jpg", "b.jpg"):
        (tmp_path / name).write_bytes(b"fake")

    manifest = {"version": MANIFEST_VERSION, "frames": ["a.jpg", "b.jpg"]}
    (tmp_path / "quick_demo_manifest.json").write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )

    with patch("core.quick_demo.scan_quick_demo_paths") as scan:
        paths = ensure_quick_demo_paths(tmp_path, count=2)

    scan.assert_not_called()
    assert [path.name for path in paths] == ["a.jpg", "b.jpg"]


def test_ensure_quick_demo_rescans_when_manifest_missing(tmp_path: Path) -> None:
    (tmp_path / "solo.jpg").write_bytes(b"fake")

    with patch(
        "core.quick_demo.scan_quick_demo_paths",
        return_value=[tmp_path / "solo.jpg"],
    ) as scan:
        paths = ensure_quick_demo_paths(tmp_path, count=1)

    scan.assert_called_once()
    assert paths[0].name == "solo.jpg"
    saved = json.loads((tmp_path / "quick_demo_manifest.json").read_text(encoding="utf-8"))
    assert saved == {"version": MANIFEST_VERSION, "frames": ["solo.jpg"]}


def test_ensure_quick_demo_ignores_legacy_list_manifest(tmp_path: Path) -> None:
    (tmp_path / "solo.jpg").write_bytes(b"fake")
    (tmp_path / "quick_demo_manifest.json").write_text(
        json.dumps(["solo.jpg"]),
        encoding="utf-8",
    )

    with patch(
        "core.quick_demo.scan_quick_demo_paths",
        return_value=[tmp_path / "solo.jpg"],
    ) as scan:
        ensure_quick_demo_paths(tmp_path, count=1)

    scan.assert_called_once()
