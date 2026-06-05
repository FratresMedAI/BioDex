"""Fast tests for scripts/demo_batch.py (mocked LILA fetch + inference)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.types import AnalysisResult, BatchResult  # noqa: E402
from PIL import Image  # noqa: E402
from scripts import demo_batch  # noqa: E402


def _result(filename: str, animals: int, blank: bool = False) -> AnalysisResult:
    return AnalysisResult(
        detections=[],
        total=animals,
        animal_count=animals,
        person_count=0,
        vehicle_count=0,
        is_blank=blank,
        threshold=0.25,
        species_enabled=True,
        filename=filename,
        summary="ok",
        image_width=100,
        image_height=100,
    )


def _volume_batch() -> BatchResult:
    return BatchResult(
        results=[
            _result("a.jpg", 3),
            _result("b.jpg", 2),
            _result("c.jpg", 1),
            _result("d.jpg", 0, blank=True),
        ],
        failed=[],
        total_images=4,
        processed_count=4,
        blank_count=1,
        total_detections=6,
        animal_count=6,
        person_count=0,
        vehicle_count=0,
        species_counts={"Island Fox": 4, "Bird": 2},
        threshold=0.25,
        species_enabled=True,
    )


def test_select_demo_filenames_mixes_multi_and_blanks() -> None:
    metadata = {
        "categories": [
            {"id": 1, "name": "empty"},
            {"id": 2, "name": "fox"},
        ],
        "images": [
            {"id": 1, "file_name": "blank.jpg"},
            {"id": 2, "file_name": "single.jpg"},
            {"id": 3, "file_name": "multi.jpg"},
        ],
        "annotations": [
            {"image_id": 1, "category_id": 1},
            {"image_id": 2, "category_id": 2},
            {"image_id": 3, "category_id": 2},
            {"image_id": 3, "category_id": 2},
            {"image_id": 3, "category_id": 2},
        ],
    }
    selected = demo_batch.select_demo_filenames(
        metadata,
        max_images=3,
        multi_animal_quota=1,
        blank_quota=1,
        single_animal_quota=1,
        seed=0,
    )
    assert "multi.jpg" in selected
    assert "blank.jpg" in selected
    assert len(selected) == 3


def test_format_volume_summary_includes_blank_rate_and_multi_animal() -> None:
    batch = _volume_batch()
    text = demo_batch.format_volume_summary(
        batch,
        dataset="Test Dataset",
        image_dir=Path("/tmp/images"),
        csv_path="/tmp/out.csv",
        json_path="/tmp/out.json",
        zip_path="/tmp/out.zip",
        show_species=True,
    )
    assert "=== BioDex Volume Batch Demo ===" in text
    assert "Images with 2+ animals detected: 2" in text
    assert "Blanks: 1 (25.0%)" in text
    assert "Top species:" in text


@patch("scripts.demo_batch.run_batch")
@patch("scripts.demo_batch.ensure_volume_images")
def test_run_volume_demo_passes_with_credible_totals(
    mock_ensure: MagicMock,
    mock_run_batch: MagicMock,
    tmp_path: Path,
) -> None:
    image_dir = tmp_path / "cache"
    image_dir.mkdir()
    (image_dir / "a.jpg").write_bytes(b"fake")
    mock_ensure.return_value = image_dir
    mock_run_batch.return_value = _volume_batch()

    output_dir = tmp_path / "out"
    csv_path = output_dir / "batch_summary.csv"
    json_path = output_dir / "batch_summary.json"
    zip_path = output_dir / "batch_annotated.zip"

    with (
        patch("scripts.demo_batch.batch_smoke.load_example_images") as mock_load,
        patch(
            "scripts.demo_batch.batch_smoke.export_batch_artifacts",
            return_value=(str(csv_path), str(json_path), str(zip_path)),
        ),
    ):
        mock_load.return_value = [("a.jpg", Image.new("RGB", (10, 10)))]
        for path in (csv_path, json_path, zip_path):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("data", encoding="utf-8")

        code = demo_batch.run_volume_demo(
            cache_dir=image_dir,
            output_dir=output_dir,
            threshold=0.25,
            classify_species=True,
            max_images=4,
            multi_animal_quota=2,
            blank_quota=1,
            single_animal_quota=1,
            min_animals=5,
            min_multi_animal_images=2,
            seed=0,
            workers=1,
            refresh=False,
        )

    assert code == 0
    mock_run_batch.assert_called_once()
