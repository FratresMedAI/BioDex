"""
MegaDetector v5a inference and BioDex analysis pipeline.

Note: This package is named ``core`` (not ``utils``) because MegaDetector's
YOLOv5 backend imports ``utils.general`` — a top-level ``utils`` package
would shadow that module and break detection.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from PIL import Image

from core.classifier import enrich_with_species
from core.types import (
    ANIMAL_CATEGORY_ID,
    CATEGORY_MAP,
    PERSON_CATEGORY_ID,
    VEHICLE_CATEGORY_ID,
    AnalysisResult,
    DetectionRecord,
    get_category_label,
)

MODEL_ID = "MDV5A"

_detector = None


def get_detector():
    """Return a cached MegaDetector model instance (loads once per process)."""
    global _detector
    if _detector is None:
        try:
            from megadetector.detection import run_detector

            _detector = run_detector.load_detector(MODEL_ID)
        except Exception as exc:
            raise RuntimeError(
                "Failed to load MegaDetector. If this is your first run, "
                "model weights may still be downloading (~280 MB)."
            ) from exc
    return _detector


def _ensure_rgb_image(image: Image.Image) -> Image.Image:
    """Validate and normalize a PIL image for inference."""
    if not isinstance(image, Image.Image):
        raise ValueError("Expected a PIL Image for analysis.")

    try:
        image.load()
    except Exception as exc:
        raise ValueError("Could not read the uploaded image. It may be corrupt.") from exc

    if image.mode != "RGB":
        image = image.convert("RGB")
    return image


def _pil_to_numpy(image: Image.Image) -> np.ndarray:
    """Convert PIL RGB image to numpy array expected by MegaDetector."""
    return np.array(image)


def _run_megadetector(image: Image.Image, threshold: float) -> list[dict[str, Any]]:
    """Run MegaDetector and return detections above threshold."""
    model = get_detector()
    raw = model.generate_detections_one_image(
        _pil_to_numpy(image),
        detection_threshold=threshold,
    )
    all_detections: list[dict[str, Any]] = raw.get("detections", [])
    return [d for d in all_detections if float(d.get("conf", 0.0)) >= threshold]


def _build_detection_records(raw_detections: list[dict[str, Any]]) -> list[DetectionRecord]:
    """Convert MegaDetector dicts into typed DetectionRecord objects."""
    records: list[DetectionRecord] = []
    for index, detection in enumerate(raw_detections, start=1):
        category_id = str(detection.get("category", ""))
        bbox = detection.get("bbox") or [0.0, 0.0, 0.0, 0.0]
        records.append(
            DetectionRecord(
                detection_id=index,
                category_id=category_id,
                category=get_category_label(category_id),
                confidence=float(detection.get("conf", 0.0)),
                bbox=list(bbox),
            )
        )
    return records


def _build_summary(
    *,
    threshold: float,
    animal_count: int,
    person_count: int,
    vehicle_count: int,
    is_blank: bool,
    species_enabled: bool,
    detections: list[DetectionRecord],
    species_warning: str,
) -> str:
    """Build a plain-English summary for the results panel."""
    if is_blank:
        summary = (
            f"No animals, people, or vehicles detected above the "
            f"{threshold:.2f} confidence threshold. This image is likely a blank."
        )
    else:
        parts: list[str] = []
        if animal_count:
            parts.append(f"{animal_count} animal{'s' if animal_count != 1 else ''}")
        if person_count:
            parts.append(f"{person_count} person{'s' if person_count != 1 else ''}")
        if vehicle_count:
            parts.append(f"{vehicle_count} vehicle{'s' if vehicle_count != 1 else ''}")

        summary = (
            f"Detected {', '.join(parts)} at >={threshold:.2f} confidence. "
            "Review bounding boxes on the annotated image."
        )

    if species_enabled and not is_blank:
        species_hits = [
            d.species for d in detections if d.category_id == ANIMAL_CATEGORY_ID and d.species
        ]
        if species_hits:
            top = max(species_hits, key=lambda s: s.confidence)
            summary += f" Top species: {top.label} ({top.confidence:.2f})."
        elif species_warning:
            summary += f" {species_warning}"
        else:
            summary += " Species classification returned no confident labels for animal crops."

    return summary


def run_analysis(
    image: Image.Image,
    threshold: float = 0.25,
    classify_species: bool = False,
    filename: str = "upload",
) -> AnalysisResult:
    """
    Run the full BioDex analysis pipeline on a single image.

    Args:
        image: Camera trap image (JPG/PNG).
        threshold: Minimum confidence to keep a detection.
        classify_species: Whether to run SpeciesNet on animal crops.
        filename: Source filename used in exports.

    Returns:
        AnalysisResult with counts, detections, and summary text.
    """
    image = _ensure_rgb_image(image)
    raw_detections = _run_megadetector(image, threshold)
    detections = _build_detection_records(raw_detections)

    species_warning = ""
    if classify_species and detections:
        detections, species_warning = enrich_with_species(image, detections, filename)

    animal_count = sum(1 for d in detections if d.category_id == ANIMAL_CATEGORY_ID)
    person_count = sum(1 for d in detections if d.category_id == PERSON_CATEGORY_ID)
    vehicle_count = sum(1 for d in detections if d.category_id == VEHICLE_CATEGORY_ID)
    is_blank = len(detections) == 0

    summary = _build_summary(
        threshold=threshold,
        animal_count=animal_count,
        person_count=person_count,
        vehicle_count=vehicle_count,
        is_blank=is_blank,
        species_enabled=classify_species,
        detections=detections,
        species_warning=species_warning,
    )

    return AnalysisResult(
        detections=detections,
        total=len(detections),
        animal_count=animal_count,
        person_count=person_count,
        vehicle_count=vehicle_count,
        is_blank=is_blank,
        threshold=threshold,
        species_enabled=classify_species,
        filename=filename,
        summary=summary,
        species_warning=species_warning,
    )


# Backward-compatible alias for v1 callers/tests.
def run_detection(image: Image.Image, threshold: float = 0.25) -> AnalysisResult:
    """Legacy entry point — detection only, no species classification."""
    return run_analysis(image, threshold=threshold, classify_species=False)


__all__ = [
    "ANIMAL_CATEGORY_ID",
    "CATEGORY_MAP",
    "MODEL_ID",
    "get_category_label",
    "get_detector",
    "run_analysis",
    "run_detection",
]
