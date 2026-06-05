"""Unit tests for core.detector image prep and analysis (mocked inference)."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
from PIL import Image, ImageOps

from core.detector import (
    _build_detection_records,
    _prepare_camera_trap_image,
    _run_megadetector,
    analyze_single_image,
)
from core.types import ANIMAL_CATEGORY_ID, AnalysisResult


class _FakeDetector:
    """Minimal MegaDetector stand-in for unit tests."""

    def __init__(self, detections: list[dict[str, Any]] | None = None) -> None:
        self._detections = detections or []

    def generate_detections_one_image(
        self,
        _image_array: object,
        detection_threshold: float = 0.25,
    ) -> dict[str, list[dict[str, Any]]]:
        filtered = [
            d for d in self._detections if float(d.get("conf", 0.0)) >= detection_threshold
        ]
        return {"detections": filtered}


@pytest.fixture
def rgb_image() -> Image.Image:
    return Image.new("RGB", (64, 48), color=(120, 80, 40))


@pytest.fixture
def sample_detection() -> dict[str, Any]:
    return {
        "category": ANIMAL_CATEGORY_ID,
        "conf": 0.9,
        "bbox": [0.1, 0.2, 0.3, 0.4],
    }


def test_prepare_camera_trap_image_converts_non_rgb() -> None:
    gray = Image.new("L", (10, 10), color=128)
    prepared = _prepare_camera_trap_image(gray)
    assert prepared.mode == "RGB"
    assert prepared.size == (10, 10)


def test_prepare_camera_trap_image_rejects_non_pil() -> None:
    with pytest.raises(ValueError, match="Expected a PIL Image"):
        _prepare_camera_trap_image("not-an-image")  # type: ignore[arg-type]


def test_prepare_camera_trap_image_rejects_corrupt(monkeypatch: pytest.MonkeyPatch) -> None:
    image = Image.new("RGB", (8, 8))
    monkeypatch.setattr(image, "load", MagicMock(side_effect=OSError("truncated")))

    with pytest.raises(ValueError, match="corrupt"):
        _prepare_camera_trap_image(image)


def test_prepare_camera_trap_image_rejects_zero_dimensions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = MagicMock()
    fake.mode = "RGB"
    fake.size = (0, 4)
    fake.load.return_value = None
    fake.convert.return_value = fake
    monkeypatch.setattr(ImageOps, "exif_transpose", lambda _img: fake)

    with pytest.raises(ValueError, match="invalid dimensions"):
        _prepare_camera_trap_image(Image.new("RGB", (4, 4)))


def test_build_detection_records_bbox_edges() -> None:
    raw = [
        {"category": "1", "conf": 0.5, "bbox": [0.0, 0.0, 1.0, 1.0]},
        {"category": "1", "conf": 0.4, "bbox": [-0.1, -0.2, 0.5, 0.5]},
        {"category": "1", "conf": 0.3},  # missing bbox defaults
    ]
    records = _build_detection_records(raw)
    assert len(records) == 3
    assert records[0].bbox == [0.0, 0.0, 1.0, 1.0]
    assert records[1].bbox == [-0.1, -0.2, 0.5, 0.5]
    assert records[2].bbox == [0.0, 0.0, 0.0, 0.0]


def test_run_megadetector_threshold_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    detections = [
        {"category": "1", "conf": 0.01, "bbox": [0, 0, 0.1, 0.1]},
        {"category": "2", "conf": 0.99, "bbox": [0.2, 0.2, 0.1, 0.1]},
    ]
    monkeypatch.setattr(
        "core.detector.get_detector",
        lambda: _FakeDetector(detections),
    )
    image = Image.new("RGB", (20, 20))
    out = _run_megadetector(image, threshold=0.0)
    assert len(out) == 2


def test_run_megadetector_threshold_one(monkeypatch: pytest.MonkeyPatch) -> None:
    detections = [
        {"category": "1", "conf": 0.99, "bbox": [0, 0, 0.1, 0.1]},
        {"category": "1", "conf": 0.5, "bbox": [0.2, 0.2, 0.1, 0.1]},
    ]
    monkeypatch.setattr(
        "core.detector.get_detector",
        lambda: _FakeDetector(detections),
    )
    image = Image.new("RGB", (20, 20))
    out = _run_megadetector(image, threshold=1.0)
    assert out == []


def test_analyze_single_image_blank(
    monkeypatch: pytest.MonkeyPatch,
    rgb_image: Image.Image,
) -> None:
    monkeypatch.setattr("core.detector.get_detector", lambda: _FakeDetector([]))
    result = analyze_single_image(rgb_image, threshold=0.25, classify_species=False)
    assert result.is_blank is True
    assert result.total == 0
    assert "blank" in result.summary.lower()
    assert result.model_id == "MDV5A"
    assert result.inference_ms is not None
    assert result.timestamp == result.analyzed_at


def test_analyze_single_image_species_disabled(
    monkeypatch: pytest.MonkeyPatch,
    rgb_image: Image.Image,
    sample_detection: dict[str, Any],
) -> None:
    monkeypatch.setattr(
        "core.detector.get_detector",
        lambda: _FakeDetector([sample_detection]),
    )
    enrich = MagicMock(side_effect=AssertionError("species should not run"))
    monkeypatch.setattr("core.detector.enrich_with_species", enrich)

    result = analyze_single_image(rgb_image, classify_species=False)
    assert result.species_enabled is False
    assert result.animal_count == 1
    enrich.assert_not_called()


def test_analyze_single_image_species_enabled(
    monkeypatch: pytest.MonkeyPatch,
    rgb_image: Image.Image,
    sample_detection: dict[str, Any],
) -> None:
    from core.types import DetectionRecord, SpeciesPrediction

    enriched = DetectionRecord(
        detection_id=1,
        category_id=ANIMAL_CATEGORY_ID,
        category="animal",
        confidence=0.9,
        bbox=[0.1, 0.2, 0.3, 0.4],
        species=SpeciesPrediction(label="Ocelot", confidence=0.88),
    )
    monkeypatch.setattr(
        "core.detector.get_detector",
        lambda: _FakeDetector([sample_detection]),
    )
    monkeypatch.setattr(
        "core.detector.enrich_with_species",
        lambda *_args, **_kwargs: ([enriched], []),
    )

    result = analyze_single_image(rgb_image, classify_species=True)
    assert result.species_enabled is True
    assert result.detections[0].species is not None
    assert result.detections[0].species.label == "Ocelot"


def test_analyze_single_image_classification_failure_warning(
    monkeypatch: pytest.MonkeyPatch,
    rgb_image: Image.Image,
    sample_detection: dict[str, Any],
) -> None:
    from core.types import DetectionRecord

    detection = DetectionRecord(
        detection_id=1,
        category_id=ANIMAL_CATEGORY_ID,
        category="animal",
        confidence=0.9,
        bbox=[0.1, 0.2, 0.3, 0.4],
    )
    monkeypatch.setattr(
        "core.detector.get_detector",
        lambda: _FakeDetector([sample_detection]),
    )
    monkeypatch.setattr(
        "core.detector.enrich_with_species",
        lambda *_args, **_kwargs: (
            [detection],
            ["Species classification failed during inference."],
        ),
    )

    result = analyze_single_image(rgb_image, classify_species=True)
    assert any("Species classification failed" in w for w in result.warnings)


def test_run_megadetector_inference_failure(
    monkeypatch: pytest.MonkeyPatch,
    rgb_image: Image.Image,
) -> None:
    class _BrokenDetector:
        def generate_detections_one_image(self, *_args: object, **_kwargs: object) -> None:
            raise RuntimeError("GPU OOM")

    monkeypatch.setattr("core.detector.get_detector", lambda: _BrokenDetector())

    with pytest.raises(RuntimeError, match="MegaDetector inference failed"):
        _run_megadetector(rgb_image, threshold=0.25)


@pytest.mark.slow
def test_analyze_single_image_live_smoke() -> None:
    """Optional live inference when MegaDetector is installed."""
    pytest.importorskip("megadetector")
    image = Image.new("RGB", (128, 96), color=(90, 70, 50))
    result: AnalysisResult = analyze_single_image(image, classify_species=False)
    assert result.inference_ms is not None
