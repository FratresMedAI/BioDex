"""Unit tests for export helpers."""

import json
from pathlib import Path

from core.exports import detections_to_csv, export_json
from core.types import AnalysisResult, DetectionRecord, SpeciesPrediction


def _sample_result() -> AnalysisResult:
    detection = DetectionRecord(
        detection_id=1,
        category_id="1",
        category="animal",
        confidence=0.91,
        bbox=[0.1, 0.2, 0.3, 0.4],
        species=SpeciesPrediction(
            label="Ocelot",
            confidence=0.98,
            top3=[("Ocelot", 0.98), ("Felidae", 0.01)],
        ),
    )
    return AnalysisResult(
        detections=[detection],
        total=1,
        animal_count=1,
        person_count=0,
        vehicle_count=0,
        is_blank=False,
        threshold=0.25,
        species_enabled=True,
        filename="sample.jpg",
        summary="test summary",
    )


def test_detections_to_csv():
    result = _sample_result()
    path = detections_to_csv(result)
    try:
        text = Path(path).read_text(encoding="utf-8")
        assert "sample.jpg" in text
        assert "Ocelot" in text
        assert "detection_id" in text.splitlines()[0]
    finally:
        Path(path).unlink(missing_ok=True)


def test_export_json():
    result = _sample_result()
    path = export_json(result)
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        assert payload["biodex_version"] == "0.2"
        assert payload["counts"]["animals"] == 1
        assert payload["detections"][0]["species"]["label"] == "Ocelot"
    finally:
        Path(path).unlink(missing_ok=True)
