"""
MegaDetector v5a inference and BioDex analysis pipeline (facade).

Note: This package is named ``core`` (not ``utils``) because MegaDetector's
YOLOv5 backend imports ``utils.general`` — a top-level ``utils`` package
would shadow that module and break detection.
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Callable
from typing import Any

from PIL import Image

from core.config import get_model_settings
from core.models import base as _models_base
from core.models.megadetector import (
    build_detection_records,
    prepare_camera_trap_image,
)
from core.models.registry import get_classifier as _registry_get_classifier
from core.models.registry import get_detector as _registry_get_detector
from core.types import (
    ANIMAL_CATEGORY_ID,
    CATEGORY_MAP,
    DEFAULT_SPECIES_MIN_CONFIDENCE,
    MODEL_ID,
    PERSON_CATEGORY_ID,
    SPECIES_TIER_BORDERLINE,
    SPECIES_TIER_UNCERTAIN,
    VEHICLE_CATEGORY_ID,
    AnalysisResult,
    DetectionRecord,
    format_species_display,
    utc_now_iso,
)

ProgressCallback = Callable[[str], None] | None

logger = logging.getLogger(__name__)

# Backwards-compatible re-exports for tests and internal callers.
_prepare_camera_trap_image = prepare_camera_trap_image
_build_detection_records = build_detection_records


def get_detector() -> Any:
    """Return a cached MegaDetector model instance (loads once per process)."""
    adapter = _registry_get_detector()
    if not adapter.is_loaded:
        adapter.load()
    return getattr(adapter, "_model", adapter)


def _run_megadetector(
    image: Image.Image,
    threshold: float,
    *,
    detector: _models_base.BaseDetector | None = None,
) -> list[dict[str, Any]]:
    """Run MegaDetector and return detections at or above ``threshold``."""
    backend = detector or _registry_get_detector()
    return backend.predict(image, threshold)


def _build_summary(
    *,
    threshold: float,
    animal_count: int,
    person_count: int,
    vehicle_count: int,
    is_blank: bool,
    species_enabled: bool,
    detections: list[DetectionRecord],
    warnings: list[str],
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
            d.species
            for d in detections
            if d.category_id == ANIMAL_CATEGORY_ID and d.species
        ]
        if species_hits:
            top = max(species_hits, key=lambda s: s.confidence)
            display = format_species_display(top)
            summary += f" Top species: {display}."
            if top.confidence_tier == SPECIES_TIER_BORDERLINE:
                summary += " Species confidence is borderline — review alternatives."
            elif top.confidence_tier == SPECIES_TIER_UNCERTAIN:
                summary += " Species ID is uncertain — expert review recommended."
        elif warnings:
            summary += f" {warnings[0]}"
        else:
            summary += " Species classification returned no confident labels for animal crops."

    return summary


def analyze_single_image(
    image: Image.Image,
    threshold: float = 0.25,
    classify_species: bool = False,
    filename: str = "upload",
    species_min_confidence: float = DEFAULT_SPECIES_MIN_CONFIDENCE,
    progress_callback: ProgressCallback = None,
    *,
    detector: _models_base.BaseDetector | None = None,
    classifier: _models_base.BaseClassifier | None = None,
) -> AnalysisResult:
    """
    Run the full BioDex analysis pipeline on a single image.

    Args:
        image: Camera trap image (JPG/PNG).
        threshold: Minimum confidence to keep a detection.
        classify_species: Whether to run SpeciesNet on animal crops.
        filename: Source filename used in exports.
        species_min_confidence: Minimum species score before labeling as Uncertain.
        progress_callback: Optional ``(message)`` hook for UI progress updates.
        detector: Optional detector backend (default: registry).
        classifier: Optional classifier backend (default: registry).

    Returns:
        AnalysisResult with counts, detections, metadata, and summary text.
    """
    image = prepare_camera_trap_image(image)
    width, height = image.size
    analyzed_at = utc_now_iso()
    settings = get_model_settings()
    backend = detector or _registry_get_detector()
    model_id = getattr(backend, "model_id", MODEL_ID)

    logger.info(
        "Analyzing %s (%dx%d) threshold=%.2f species=%s",
        filename,
        width,
        height,
        threshold,
        classify_species,
    )
    warnings: list[str] = []
    t0 = time.perf_counter()

    if progress_callback:
        progress_callback("Loading MegaDetector and running detection…")

    raw_detections = _run_megadetector(image, threshold, detector=backend)
    detections = backend.build_records(raw_detections)

    species_warning = ""
    if classify_species and detections:
        animal_count = sum(1 for d in detections if d.category_id == ANIMAL_CATEGORY_ID)
        if progress_callback and animal_count:
            progress_callback(f"Running SpeciesNet on {animal_count} animal crop(s)…")
        cls_backend = classifier or _registry_get_classifier()
        detections, species_warnings = cls_backend.enrich(
            image,
            detections,
            filename,
            species_min_confidence=species_min_confidence,
            geofence_region=settings.geofence_region,
        )
        warnings.extend(species_warnings)
        species_warning = species_warnings[0] if species_warnings else ""

    inference_ms = (time.perf_counter() - t0) * 1000.0

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
        warnings=warnings,
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
        image_width=width,
        image_height=height,
        analyzed_at=analyzed_at,
        warnings=warnings,
        species_warning=species_warning,
        model_id=model_id,
        inference_ms=round(inference_ms, 2),
        timestamp=analyzed_at,
    )


def run_analysis(
    image: Image.Image,
    threshold: float = 0.25,
    classify_species: bool = False,
    filename: str = "upload",
    species_min_confidence: float = DEFAULT_SPECIES_MIN_CONFIDENCE,
    progress_callback: ProgressCallback = None,
) -> AnalysisResult:
    """Backward-compatible alias for ``analyze_single_image``."""
    return analyze_single_image(
        image,
        threshold=threshold,
        classify_species=classify_species,
        filename=filename,
        species_min_confidence=species_min_confidence,
        progress_callback=progress_callback,
    )


def run_detection(image: Image.Image, threshold: float = 0.25) -> AnalysisResult:
    """Legacy entry point — detection only, no species classification."""
    return analyze_single_image(image, threshold=threshold, classify_species=False)


def warmup_models(*, species: bool = False) -> None:
    """Eager-load MegaDetector (and optionally SpeciesNet) before the first frame."""
    try:
        import torch

        threads = min(8, os.cpu_count() or 4)
        torch.set_num_threads(threads)
    except Exception:
        pass
    adapter = _registry_get_detector()
    adapter.load()
    if species:
        _registry_get_classifier().load()


def get_category_label(category_id: str) -> str:
    """Map MegaDetector category ID to a readable label."""
    from core.types import get_category_label as _label

    return _label(category_id)


__all__ = [
    "ANIMAL_CATEGORY_ID",
    "CATEGORY_MAP",
    "MODEL_ID",
    "ProgressCallback",
    "_build_detection_records",
    "_prepare_camera_trap_image",
    "_run_megadetector",
    "analyze_single_image",
    "get_category_label",
    "get_detector",
    "warmup_models",
    "run_analysis",
    "run_detection",
]
