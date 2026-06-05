"""
MegaDetector v5a inference and BioDex analysis pipeline.

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

import numpy as np
import numpy.typing as npt
from PIL import Image, ImageOps

from core.classifier import enrich_with_species
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
    get_category_label,
    utc_now_iso,
)

ProgressCallback = Callable[[str], None] | None

logger = logging.getLogger(__name__)

_detector = None


def get_detector() -> Any:
    """Return a cached MegaDetector model instance (loads once per process)."""
    global _detector
    if _detector is None:
        try:
            from megadetector.detection import run_detector

            logger.info("Loading MegaDetector model %s…", MODEL_ID)
            _detector = run_detector.load_detector(MODEL_ID)
            logger.info("MegaDetector ready.")
        except Exception as exc:
            logger.exception("MegaDetector load failed")
            raise RuntimeError(
                "Failed to load MegaDetector. If this is your first run, "
                "model weights may still be downloading (~280 MB). "
                f"Details: {exc}"
            ) from exc
    return _detector


def _prepare_camera_trap_image(image: Image.Image) -> Image.Image:
    """
    Normalize a camera trap image for detection and display.

    Fixes EXIF orientation (common on trail cameras), validates pixels,
    and converts to RGB without downscaling.
    """
    if not isinstance(image, Image.Image):
        raise ValueError("Expected a PIL Image for analysis.")

    try:
        image.load()
    except Exception as exc:
        raise ValueError("Could not read the uploaded image. It may be corrupt.") from exc

    image = ImageOps.exif_transpose(image)
    if image.mode != "RGB":
        try:
            image = image.convert("RGB")
        except Exception as exc:
            raise ValueError("Could not convert image to RGB.") from exc

    width, height = image.size
    if width <= 0 or height <= 0:
        raise ValueError("Image has invalid dimensions (width and height must be > 0).")
    return image


def _pil_to_numpy(image: Image.Image) -> npt.NDArray[Any]:
    """Convert PIL RGB image to numpy array expected by MegaDetector."""
    return np.array(image)


def _run_megadetector(image: Image.Image, threshold: float) -> list[dict[str, Any]]:
    """
    Run MegaDetector and return detections at or above ``threshold``.

    MegaDetector receives ``detection_threshold`` and results are filtered again
    so the UI threshold is applied consistently.
    """
    model = get_detector()
    try:
        raw = model.generate_detections_one_image(
            _pil_to_numpy(image),
            detection_threshold=threshold,
        )
    except Exception as exc:
        logger.exception("MegaDetector inference failed")
        raise RuntimeError(
            "MegaDetector inference failed. Check model weights and image format. "
            f"Details: {exc}"
        ) from exc
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

    Returns:
        AnalysisResult with counts, detections, metadata, and summary text.
    """
    image = _prepare_camera_trap_image(image)
    width, height = image.size
    analyzed_at = utc_now_iso()
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

    raw_detections = _run_megadetector(image, threshold)
    detections = _build_detection_records(raw_detections)

    species_warning = ""
    if classify_species and detections:
        animal_count = sum(1 for d in detections if d.category_id == ANIMAL_CATEGORY_ID)
        if progress_callback and animal_count:
            progress_callback(f"Running SpeciesNet on {animal_count} animal crop(s)…")
        detections, species_warnings = enrich_with_species(
            image,
            detections,
            filename,
            species_min_confidence=species_min_confidence,
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
        model_id=MODEL_ID,
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
    get_detector()
    if species:
        from core.classifier import get_classifier

        get_classifier()


__all__ = [
    "ANIMAL_CATEGORY_ID",
    "CATEGORY_MAP",
    "MODEL_ID",
    "ProgressCallback",
    "analyze_single_image",
    "get_category_label",
    "get_detector",
    "warmup_models",
    "run_analysis",
    "run_detection",
]
