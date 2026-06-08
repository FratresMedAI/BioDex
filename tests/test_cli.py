"""Tests for core.cli batch command (mocked inference)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from core.cli import run_batch_cli
from core.types import AnalysisResult, BatchResult
from PIL import Image


def _result(filename: str, animals: int, *, error: str = "") -> AnalysisResult:
    return AnalysisResult(
        detections=[],
        total=animals,
        animal_count=animals,
        person_count=0,
        vehicle_count=0,
        is_blank=animals == 0,
        threshold=0.25,
        species_enabled=False,
        filename=filename,
        summary="ok",
        image_width=100,
        image_height=100,
        error=error,
    )


def _batch() -> BatchResult:
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
        species_counts={},
        threshold=0.25,
        species_enabled=False,
    )


@patch("core.cli.build_batch_annotated_zip", return_value=None)
@patch("core.cli.export_batch_json", return_value="/tmp/t.json")
@patch("core.cli.batch_to_csv", return_value="/tmp/t.csv")
@patch("core.cli.run_batch_from_paths")
def test_run_batch_cli_writes_summary_and_report(
    mock_run_batch: MagicMock,
    mock_csv: MagicMock,
    mock_json: MagicMock,
    mock_zip: MagicMock,
    tmp_path: Path,
) -> None:
    input_dir = tmp_path / "in"
    output_dir = tmp_path / "out"
    input_dir.mkdir()
    (input_dir / "a.jpg").write_bytes(b"\xff\xd8\xff")
    (input_dir / "b.jpg").write_bytes(b"\xff\xd8\xff")

    mock_run_batch.return_value = _batch()
    csv_tmp = tmp_path / "t.csv"
    json_tmp = tmp_path / "t.json"
    csv_tmp.write_text("csv", encoding="utf-8")
    json_tmp.write_text("{}", encoding="utf-8")
    mock_csv.return_value = str(csv_tmp)
    mock_json.return_value = str(json_tmp)

    with (
        patch("core.cli.Image.open") as mock_open,
        patch("core.cli.draw_detections") as mock_draw,
        patch("core.cli.save_annotated_image", return_value=str(tmp_path / "a.png")),
        patch("core.cli.detections_to_csv", return_value=str(tmp_path / "a.csv")),
        patch("core.cli.export_json", return_value=str(tmp_path / "a.json")),
        patch("core.cli.shutil.move"),
    ):
        mock_open.return_value.__enter__.return_value.convert.return_value = Image.new(
            "RGB", (10, 10)
        )
        mock_draw.return_value = Image.new("RGB", (10, 10))
        code = run_batch_cli(input_dir, output_dir, recursive=False, verbose=False)

    assert code == 0
    assert (output_dir / "batch_report.txt").is_file()
    mock_run_batch.assert_called_once()


@patch("core.cli.run_batch_from_paths")
def test_run_batch_cli_returns_partial_failure_code(
    mock_run_batch: MagicMock,
    tmp_path: Path,
) -> None:
    input_dir = tmp_path / "in"
    output_dir = tmp_path / "out"
    input_dir.mkdir()
    (input_dir / "a.jpg").write_bytes(b"\xff\xd8\xff")

    batch = _batch()
    batch = BatchResult(
        results=[_result("a.jpg", 0, error="boom")],
        failed=[("a.jpg", "boom")],
        total_images=1,
        processed_count=1,
        blank_count=0,
        total_detections=0,
        animal_count=0,
        person_count=0,
        vehicle_count=0,
        species_counts={},
        threshold=0.25,
        species_enabled=False,
    )
    mock_run_batch.return_value = batch

    with (
        patch("core.cli.batch_to_csv", return_value=str(tmp_path / "t.csv")),
        patch("core.cli.export_batch_json", return_value=str(tmp_path / "t.json")),
        patch("core.cli.build_batch_annotated_zip", return_value=None),
        patch("core.cli.Image.open") as mock_open,
    ):
        mock_open.return_value.__enter__.return_value.convert.return_value = Image.new(
            "RGB", (10, 10)
        )
        Path(tmp_path / "t.csv").write_text("x", encoding="utf-8")
        Path(tmp_path / "t.json").write_text("{}", encoding="utf-8")
        code = run_batch_cli(input_dir, output_dir, recursive=False)

    assert code == 2
