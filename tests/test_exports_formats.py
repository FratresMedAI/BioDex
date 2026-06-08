"""Tests for advanced export formats."""

from __future__ import annotations

from core.exports import (
    export_ecosentinel,
    export_inaturalist,
    export_sqlite,
    export_timelapse_md,
    export_wildlife_insights,
)
from core.types import AnalysisResult, BatchResult, DetectionRecord, SpeciesPrediction


def _sample_batch() -> BatchResult:
    detection = DetectionRecord(
        detection_id=1,
        category_id="1",
        category="animal",
        confidence=0.9,
        bbox=[0.1, 0.2, 0.3, 0.4],
        species=SpeciesPrediction(label="Deer", confidence=0.85),
    )
    result = AnalysisResult(
        detections=[detection],
        total=1,
        animal_count=1,
        person_count=0,
        vehicle_count=0,
        is_blank=False,
        threshold=0.25,
        species_enabled=True,
        filename="test.jpg",
        summary="ok",
        model_id="MDV5A",
    )
    return BatchResult(
        results=[result],
        failed=[],
        total_images=1,
        processed_count=1,
        blank_count=0,
        total_detections=1,
        animal_count=1,
        person_count=0,
        vehicle_count=0,
        species_counts={"Deer": 1},
    )


def test_export_wildlife_insights(tmp_path) -> None:
    path = export_wildlife_insights(_sample_batch())
    assert path.endswith(".csv")


def test_export_inaturalist() -> None:
    path = export_inaturalist(_sample_batch())
    with open(path, encoding="utf-8") as handle:
        content = handle.read()
    assert "MANUAL REVIEW" in content


def test_export_timelapse_md() -> None:
    path = export_timelapse_md(_sample_batch())
    assert path.endswith(".json")


def test_export_sqlite(tmp_path) -> None:
    db = tmp_path / "test.sqlite"
    path = export_sqlite(_sample_batch(), db)
    assert path.endswith(".sqlite")


def test_export_ecosentinel() -> None:
    path = export_ecosentinel(_sample_batch())
    assert path.endswith(".json")
