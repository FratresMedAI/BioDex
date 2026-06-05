"""Fast tests for scripts/batch_smoke.py (mocked inference)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.types import AnalysisResult, BatchResult  # noqa: E402
from PIL import Image  # noqa: E402
from scripts import batch_smoke  # noqa: E402


def _result(filename: str, animals: int) -> AnalysisResult:
    return AnalysisResult(
        detections=[],
        total=animals,
        animal_count=animals,
        person_count=0,
        vehicle_count=0,
        is_blank=animals == 0,
        threshold=0.25,
        species_enabled=True,
        filename=filename,
        summary="ok",
        image_width=100,
        image_height=100,
    )


def _fake_batch() -> BatchResult:
    return BatchResult(
        results=[_result("a.jpg", 2), _result("b.jpg", 1)],
        failed=[],
        total_images=2,
        processed_count=2,
        blank_count=0,
        total_detections=3,
        animal_count=3,
        person_count=0,
        vehicle_count=0,
        species_counts={"Ocelot": 2, "Deer": 1},
        threshold=0.25,
        species_enabled=True,
    )


def test_format_batch_demo_summary_includes_totals() -> None:
    batch = _fake_batch()
    text = batch_smoke.format_batch_demo_summary(
        batch,
        "/tmp/out/batch_summary.csv",
        "/tmp/out/batch_summary.json",
        "/tmp/out/batch_annotated.zip",
        show_species=True,
    )
    assert "=== BioDex Batch Demo Summary ===" in text
    assert "Images processed: 2" in text
    assert "Animals: 3" in text
    assert "Species counts:" in text
    assert "a.jpg -> 2" in text
    assert "b.jpg -> 1" in text
    assert "Master CSV:  /tmp/out/batch_summary.csv" in text
    assert "=== END ===" in text


@patch("scripts.batch_smoke.build_batch_annotated_zip")
@patch("scripts.batch_smoke.export_batch_json")
@patch("scripts.batch_smoke.batch_to_csv")
@patch("scripts.batch_smoke.run_batch")
@patch("scripts.batch_smoke.ensure_examples", return_value=0)
def test_run_batch_demo_exports_and_passes(
    mock_ensure: MagicMock,
    mock_run_batch: MagicMock,
    mock_csv: MagicMock,
    mock_json: MagicMock,
    mock_zip: MagicMock,
    tmp_path: Path,
) -> None:
    mock_run_batch.return_value = _fake_batch()
    examples = tmp_path / "examples"
    examples.mkdir()
    (examples / "a.jpg").write_bytes(b"fake")
    (examples / "b.jpg").write_bytes(b"fake")

    temp_csv = tmp_path / "temp.csv"
    temp_json = tmp_path / "temp.json"
    temp_zip = tmp_path / "temp.zip"
    temp_csv.write_text("csv-data", encoding="utf-8")
    temp_json.write_text("{}", encoding="utf-8")
    temp_zip.write_bytes(b"zip-data")
    mock_csv.return_value = str(temp_csv)
    mock_json.return_value = str(temp_json)
    mock_zip.return_value = str(temp_zip)

    output_dir = tmp_path / "out"

    with patch("scripts.batch_smoke.Image.open") as mock_open:
        mock_open.return_value.convert.return_value = Image.new("RGB", (10, 10))
        code = batch_smoke.run_batch_demo(
            examples_dir=examples,
            output_dir=output_dir,
            threshold=0.25,
            classify_species=True,
            min_animals=3,
        )

    assert code == 0
    assert (output_dir / "batch_summary.csv").read_text(encoding="utf-8") == "csv-data"
    assert (output_dir / "batch_summary.json").is_file()
    assert (output_dir / "batch_annotated.zip").read_bytes() == b"zip-data"
    mock_run_batch.assert_called_once()


@patch("scripts.batch_smoke.run_batch")
@patch("scripts.batch_smoke.ensure_examples", return_value=0)
def test_run_batch_demo_fails_below_min_animals(
    mock_ensure: MagicMock,
    mock_run_batch: MagicMock,
    tmp_path: Path,
) -> None:
    batch = _fake_batch()
    batch = BatchResult(
        results=batch.results,
        failed=batch.failed,
        total_images=batch.total_images,
        processed_count=batch.processed_count,
        blank_count=batch.blank_count,
        total_detections=1,
        animal_count=1,
        person_count=0,
        vehicle_count=0,
        species_counts=batch.species_counts,
        threshold=0.25,
        species_enabled=True,
    )
    mock_run_batch.return_value = batch

    examples = tmp_path / "examples"
    examples.mkdir()
    (examples / "a.jpg").write_bytes(b"fake")

    temp_csv = tmp_path / "t.csv"
    temp_json = tmp_path / "t.json"
    temp_csv.write_text("x", encoding="utf-8")
    temp_json.write_text("{}", encoding="utf-8")

    with (
        patch("scripts.batch_smoke.Image.open") as mock_open,
        patch("scripts.batch_smoke.batch_to_csv", return_value=str(temp_csv)),
        patch("scripts.batch_smoke.export_batch_json", return_value=str(temp_json)),
        patch("scripts.batch_smoke.build_batch_annotated_zip", return_value=None),
    ):
        mock_open.return_value.convert.return_value = Image.new("RGB", (10, 10))
        code = batch_smoke.run_batch_demo(
            examples_dir=examples,
            output_dir=tmp_path / "out",
            threshold=0.25,
            classify_species=False,
            min_animals=3,
        )

    assert code == 1
