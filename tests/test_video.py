"""Tests for video aggregation (frame extraction requires OpenCV)."""

from __future__ import annotations

from core.types import AnalysisResult, DetectionRecord
from core.video import VIDEO_SUFFIXES, aggregate_detections


def test_video_suffixes() -> None:
    assert ".mp4" in VIDEO_SUFFIXES


def test_aggregate_detections_picks_high_confidence() -> None:
    det = DetectionRecord(
        detection_id=1,
        category_id="1",
        category="animal",
        confidence=0.95,
        bbox=[0.1, 0.1, 0.2, 0.2],
    )
    result = AnalysisResult(
        detections=[det],
        total=1,
        animal_count=1,
        person_count=0,
        vehicle_count=0,
        is_blank=False,
        threshold=0.25,
        species_enabled=False,
        filename="frame.jpg",
        summary="animal",
    )
    blank = AnalysisResult(
        detections=[],
        total=0,
        animal_count=0,
        person_count=0,
        vehicle_count=0,
        is_blank=True,
        threshold=0.25,
        species_enabled=False,
        filename="blank.jpg",
        summary="blank",
    )
    keys = aggregate_detections([blank, result])
    assert len(keys) == 1
    assert keys[0][1].animal_count == 1
