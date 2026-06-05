"""Unit tests for batch analysis."""

from unittest.mock import patch

from PIL import Image

from core.batch import run_batch
from core.types import AnalysisResult, DetectionRecord


def _fake_result(filename: str, total: int) -> AnalysisResult:
    detections = []
    if total:
        detections = [
            DetectionRecord(
                detection_id=1,
                category_id="1",
                category="animal",
                confidence=0.9,
                bbox=[0.1, 0.1, 0.2, 0.2],
            )
        ]
    return AnalysisResult(
        detections=detections,
        total=total,
        animal_count=total,
        person_count=0,
        vehicle_count=0,
        is_blank=total == 0,
        threshold=0.25,
        species_enabled=False,
        filename=filename,
        summary="ok",
        image_width=100,
        image_height=100,
    )


def test_run_batch_aggregates_results():
    images = [
        ("a.jpg", Image.new("RGB", (10, 10))),
        ("b.jpg", Image.new("RGB", (10, 10))),
    ]

    with patch("core.batch.analyze_single_image") as mock_analyze:
        mock_analyze.side_effect = [
            _fake_result("a.jpg", 1),
            _fake_result("b.jpg", 0),
        ]
        batch = run_batch(images, threshold=0.25)

    assert batch.total_images == 2
    assert batch.total_detections == 1
    assert batch.blank_count == 1
    assert batch.animal_count == 1
    assert len(batch.failed) == 0


def test_run_batch_continues_on_failure():
    images = [("bad.jpg", Image.new("RGB", (10, 10)))]

    with patch("core.batch.analyze_single_image", side_effect=RuntimeError("boom")):
        batch = run_batch(images)

    assert len(batch.failed) == 1
    assert batch.failed[0][0] == "bad.jpg"
    assert batch.results[0].error == "boom"
