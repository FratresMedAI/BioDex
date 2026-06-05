"""Unit tests for visualization."""

from core.types import SPECIES_TIER_HIGH, DetectionRecord, SpeciesPrediction
from core.visualization import _adaptive_font_size, draw_detections
from PIL import Image


def test_adaptive_font_size() -> None:
    assert _adaptive_font_size(800, 600) == 12
    assert _adaptive_font_size(3200, 2400) == 22


def test_draw_detections_returns_image() -> None:
    image = Image.new("RGB", (200, 200), color=(30, 30, 30))
    detections = [
        DetectionRecord(
            detection_id=1,
            category_id="1",
            category="animal",
            confidence=0.88,
            bbox=[0.1, 0.1, 0.4, 0.4],
            species=SpeciesPrediction(
                label="Deer",
                confidence=0.91,
                top3=[("Deer", 0.91), ("Elk", 0.05)],
                confidence_tier=SPECIES_TIER_HIGH,
            ),
        ),
        DetectionRecord(
            detection_id=2,
            category_id="2",
            category="person",
            confidence=0.75,
            bbox=[0.5, 0.5, 0.2, 0.2],
        ),
    ]
    annotated = draw_detections(image, detections)
    assert annotated.size == image.size
    assert annotated.mode == "RGB"
    assert annotated.getpixel((15, 185)) != image.getpixel((15, 185))


def test_draw_detections_without_legend() -> None:
    image = Image.new("RGB", (200, 200), color=(30, 30, 30))
    detections = [
        DetectionRecord(
            detection_id=1,
            category_id="1",
            category="animal",
            confidence=0.88,
            bbox=[0.1, 0.1, 0.4, 0.4],
        ),
    ]
    with_legend = draw_detections(image, detections, show_legend=True)
    without_legend = draw_detections(image, detections, show_legend=False)
    assert with_legend.getpixel((15, 185)) != without_legend.getpixel((15, 185))


def test_draw_detections_tiny_box() -> None:
    image = Image.new("RGB", (400, 400), color=(40, 40, 40))
    detections = [
        DetectionRecord(
            detection_id=1,
            category_id="1",
            category="animal",
            confidence=0.77,
            bbox=[0.45, 0.45, 0.03, 0.03],
        ),
    ]
    annotated = draw_detections(image, detections)
    assert annotated.size == image.size


def test_draw_detections_empty() -> None:
    image = Image.new("RGB", (100, 100), color=(0, 0, 0))
    annotated = draw_detections(image, [])
    assert annotated.size == image.size
