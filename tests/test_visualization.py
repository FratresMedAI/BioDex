"""Unit tests for visualization."""

from PIL import Image

from core.types import DetectionRecord
from core.visualization import draw_detections


def test_draw_detections_returns_image():
    image = Image.new("RGB", (200, 200), color=(30, 30, 30))
    detections = [
        DetectionRecord(
            detection_id=1,
            category_id="1",
            category="animal",
            confidence=0.88,
            bbox=[0.1, 0.1, 0.4, 0.4],
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


def test_draw_detections_empty():
    image = Image.new("RGB", (100, 100), color=(0, 0, 0))
    annotated = draw_detections(image, [])
    assert annotated.size == image.size
