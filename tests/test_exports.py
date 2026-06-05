"""Unit tests for export helpers."""

import json
import zipfile
from pathlib import Path

from PIL import Image

from core.exports import (
    detections_to_csv,
    export_batch_json,
    export_bundle,
    export_json,
)
from core.types import (
    BIODEX_VERSION,
    AnalysisResult,
    BatchResult,
    DetectionRecord,
    SpeciesPrediction,
)


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
            raw_label="mammalia;leopardus_pardalis",
            confidence_tier="high",
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
        image_width=640,
        image_height=480,
        analyzed_at="2026-05-24T12:00:00+00:00",
        model_id="MDV5A",
        inference_ms=42.5,
        timestamp="2026-05-24T12:00:00+00:00",
    )


def test_detections_to_csv():
    result = _sample_result()
    path = detections_to_csv(result)
    try:
        text = Path(path).read_text(encoding="utf-8")
        assert "sample.jpg" in text
        assert "Ocelot" in text
        assert "species_tier" in text.splitlines()[0]
        assert "640" in text
    finally:
        Path(path).unlink(missing_ok=True)


def test_detections_to_csv_blank_row():
    result = AnalysisResult(
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
        image_width=100,
        image_height=100,
    )
    path = detections_to_csv(result)
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
        assert len(lines) == 2
        assert "blank.jpg" in lines[1]
        assert "True" in lines[1] or "true" in lines[1].lower()
    finally:
        Path(path).unlink(missing_ok=True)


def test_export_json():
    result = _sample_result()
    path = export_json(result)
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        assert payload["biodex_version"] == BIODEX_VERSION
        assert payload["image_width"] == 640
        assert payload["counts"]["animals"] == 1
        assert payload["detections"][0]["species"]["label"] == "Ocelot"
        assert payload["detections"][0]["species"]["confidence_tier"] == "high"
        assert payload["model_id"] == "MDV5A"
        assert payload["inference_ms"] == 42.5
        assert payload["timestamp"] == "2026-05-24T12:00:00+00:00"
    finally:
        Path(path).unlink(missing_ok=True)


def test_export_bundle():
    result = _sample_result()
    image = Image.new("RGB", (64, 64), color=(10, 20, 30))
    path = export_bundle(result, image)
    try:
        with zipfile.ZipFile(path, "r") as archive:
            names = archive.namelist()
            assert any(name.endswith("_annotated.png") for name in names)
            assert any(name.endswith("_detections.csv") for name in names)
            assert any(name.endswith("_results.json") for name in names)
    finally:
        Path(path).unlink(missing_ok=True)


def test_export_batch_json():
    result = _sample_result()
    batch = BatchResult(
        results=[result],
        failed=[],
        total_images=1,
        processed_count=1,
        blank_count=0,
        total_detections=1,
        animal_count=1,
        person_count=0,
        vehicle_count=0,
        species_counts={"Ocelot": 1},
    )
    path = export_batch_json(batch)
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        assert payload["biodex_version"] == BIODEX_VERSION
        assert payload["summary"]["species_counts"]["Ocelot"] == 1
    finally:
        Path(path).unlink(missing_ok=True)
