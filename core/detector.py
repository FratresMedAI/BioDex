"""
MegaDetector v5a inference wrapper for BioDex.

Loads MDV5A lazily on first use and runs single-image detection locally.

Note: This package is named ``core`` (not ``utils``) because MegaDetector's
YOLOv5 backend imports ``utils.general`` — a top-level ``utils`` package
would shadow that module and break detection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from PIL import Image

# MegaDetector model identifier for v5a weights (auto-downloaded on first run).
MODEL_ID = "MDV5A"

# Standard MegaDetector category IDs → human-readable labels.
CATEGORY_MAP: dict[str, str] = {
    "1": "animal",
    "2": "person",
    "3": "vehicle",
}

_detector = None


@dataclass
class DetectionResult:
    """Structured output from a single-image detection pass."""

    detections: list[dict[str, Any]] = field(default_factory=list)
    total: int = 0
    animal_count: int = 0
    person_count: int = 0
    vehicle_count: int = 0
    is_blank: bool = True
    summary: str = ""
    threshold: float = 0.25


def get_detector():
    """Return a cached MegaDetector model instance (loads once per process)."""
    global _detector
    if _detector is None:
        from megadetector.detection import run_detector

        _detector = run_detector.load_detector(MODEL_ID)
    return _detector


def _pil_to_numpy(image: Image.Image) -> np.ndarray:
    """Convert PIL RGB image to numpy array expected by MegaDetector."""
    if image.mode != "RGB":
        image = image.convert("RGB")
    return np.array(image)


def _category_label(category_id: str) -> str:
    return CATEGORY_MAP.get(str(category_id), f"unknown ({category_id})")


def _build_summary(
    *,
    threshold: float,
    animal_count: int,
    person_count: int,
    vehicle_count: int,
    is_blank: bool,
) -> str:
    """Build a short plain-English summary for the results panel."""
    if is_blank:
        return (
            f"No animals, people, or vehicles detected above the "
            f"{threshold:.2f} confidence threshold. This image is likely a blank."
        )

    parts: list[str] = []
    if animal_count:
        noun = "animal" if animal_count == 1 else "animals"
        parts.append(f"{animal_count} {noun}")
    if person_count:
        noun = "person" if person_count == 1 else "people"
        parts.append(f"{person_count} {noun}")
    if vehicle_count:
        noun = "vehicle" if vehicle_count == 1 else "vehicles"
        parts.append(f"{vehicle_count} {noun}")

    detected = ", ".join(parts)
    return (
        f"Detected {detected} at >={threshold:.2f} confidence. "
        "Review bounding boxes on the annotated image."
    )


def run_detection(image: Image.Image, threshold: float = 0.25) -> DetectionResult:
    """
    Run MegaDetector on a single PIL image and return filtered detections.

    Args:
        image: Camera trap image (JPG/PNG).
        threshold: Minimum confidence to keep a detection.

    Returns:
        DetectionResult with counts, summary, and filtered detection dicts.
    """
    model = get_detector()
    image_array = _pil_to_numpy(image)

    raw = model.generate_detections_one_image(
        image_array,
        detection_threshold=threshold,
    )

    all_detections: list[dict[str, Any]] = raw.get("detections", [])
    filtered = [d for d in all_detections if d.get("conf", 0.0) >= threshold]

    animal_count = sum(1 for d in filtered if str(d.get("category")) == "1")
    person_count = sum(1 for d in filtered if str(d.get("category")) == "2")
    vehicle_count = sum(1 for d in filtered if str(d.get("category")) == "3")
    is_blank = len(filtered) == 0

    summary = _build_summary(
        threshold=threshold,
        animal_count=animal_count,
        person_count=person_count,
        vehicle_count=vehicle_count,
        is_blank=is_blank,
    )

    return DetectionResult(
        detections=filtered,
        total=len(filtered),
        animal_count=animal_count,
        person_count=person_count,
        vehicle_count=vehicle_count,
        is_blank=is_blank,
        summary=summary,
        threshold=threshold,
    )


def get_category_label(category_id: str) -> str:
    """Public helper for display labels."""
    return _category_label(category_id)
