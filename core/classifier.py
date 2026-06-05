"""
SpeciesNet species classification for BioDex animal detections.

Loads SpeciesNet lazily on first use when species classification is enabled.
"""

from __future__ import annotations

import logging
from typing import Any

from PIL import Image

from core.types import (
    ANIMAL_CATEGORY_ID,
    DEFAULT_SPECIES_MIN_CONFIDENCE,
    SPECIES_CROP_PADDING,
    SPECIES_TIER_BORDERLINE,
    SPECIES_TIER_LOW,
    SPECIES_TIER_UNCERTAIN,
    UNCERTAIN_LABEL,
    DetectionRecord,
    SpeciesPrediction,
    format_taxon_label,
    is_blank_taxon_label,
    species_confidence_tier,
)

logger = logging.getLogger(__name__)

_classifier = None
_classifier_error: str | None = None


def get_classifier() -> Any:
    """
    Return a cached SpeciesNetClassifier instance.

    Raises RuntimeError if the classifier failed to load on a prior attempt.
    """
    global _classifier, _classifier_error

    if _classifier is not None:
        return _classifier

    if _classifier_error is not None:
        raise RuntimeError(_classifier_error)

    try:
        from speciesnet import DEFAULT_MODEL, SpeciesNetClassifier

        logger.info("Loading SpeciesNet classifier …")
        loaded = SpeciesNetClassifier(DEFAULT_MODEL)
        _classifier = loaded
        return _classifier
    except Exception as exc:
        _classifier_error = (
            "SpeciesNet failed to load. If this is your first run, model weights "
            f"may still be downloading (~214 MB). Details: {exc}"
        )
        logger.exception("SpeciesNet classifier load failed")
        raise RuntimeError(_classifier_error) from exc


def _padded_bbox(bbox: list[float], padding_ratio: float = SPECIES_CROP_PADDING) -> list[float]:
    """Expand a normalized bbox with padding for species classification."""
    xmin, ymin, box_w, box_h = bbox
    pad_x = box_w * padding_ratio
    pad_y = box_h * padding_ratio
    xmin = max(0.0, xmin - pad_x)
    ymin = max(0.0, ymin - pad_y)
    box_w = min(1.0 - xmin, box_w + 2 * pad_x)
    box_h = min(1.0 - ymin, box_h + 2 * pad_y)
    return [xmin, ymin, box_w, box_h]


def _build_top3(classes: list, scores: list) -> list[tuple[str, float]]:
    top3: list[tuple[str, float]] = []
    for raw_label, score in zip(classes[:3], scores[:3], strict=False):
        top3.append((format_taxon_label(str(raw_label)), float(score)))
    return top3


def _select_best_non_blank(top3: list[tuple[str, float]]) -> tuple[str, float, str] | None:
    """Pick the best non-blank prediction from top-3 formatted results."""
    for index, (label, score) in enumerate(top3):
        if not is_blank_taxon_label(label):
            raw = str(index)
            return label, score, raw
    return None


def apply_species_confidence_tier(
    prediction: SpeciesPrediction,
    species_min_confidence: float = DEFAULT_SPECIES_MIN_CONFIDENCE,
) -> SpeciesPrediction:
    """Apply tier labels and Uncertain marking based on confidence thresholds."""
    tier = species_confidence_tier(prediction.confidence, species_min_confidence)
    label = prediction.label

    if tier in (SPECIES_TIER_UNCERTAIN, SPECIES_TIER_LOW):
        label = UNCERTAIN_LABEL
        top3 = list(prediction.top3)
        if top3:
            top3[0] = (UNCERTAIN_LABEL, prediction.confidence)
        return SpeciesPrediction(
            label=label,
            confidence=prediction.confidence,
            top3=top3,
            raw_label=prediction.raw_label,
            confidence_tier=SPECIES_TIER_UNCERTAIN,
        )

    return SpeciesPrediction(
        label=label,
        confidence=prediction.confidence,
        top3=prediction.top3,
        raw_label=prediction.raw_label,
        confidence_tier=tier,
    )


def parse_species_result(
    result: dict,
    species_min_confidence: float = DEFAULT_SPECIES_MIN_CONFIDENCE,
) -> SpeciesPrediction | None:
    """Extract and normalize top species predictions from a SpeciesNet result dict."""
    if result.get("failures"):
        return None

    classifications = result.get("classifications", {})
    classes = classifications.get("classes") or []
    scores = classifications.get("scores") or []

    if not classes or not scores:
        return None

    top3 = _build_top3(classes, scores)
    selected = _select_best_non_blank(top3)
    if selected is None:
        return None

    best_label, best_score, raw_best = selected
    prediction = SpeciesPrediction(
        label=best_label,
        confidence=best_score,
        top3=top3,
        raw_label=str(classes[0]),
    )
    return apply_species_confidence_tier(prediction, species_min_confidence)


def _preprocess_for_detection(image: Image.Image, detection: DetectionRecord) -> Any:
    """Preprocess one animal detection for SpeciesNet batch inference."""
    from speciesnet.utils import BBox

    classifier = get_classifier()
    xmin, ymin, width, height = _padded_bbox(detection.bbox)
    bboxes = [BBox(xmin=xmin, ymin=ymin, width=width, height=height)]
    return classifier.preprocess(image, bboxes=bboxes)


def enrich_with_species(
    image: Image.Image,
    detections: list[DetectionRecord],
    filename: str,
    species_min_confidence: float = DEFAULT_SPECIES_MIN_CONFIDENCE,
) -> tuple[list[DetectionRecord], list[str]]:
    """
    Attach species predictions to animal detections in-place.

    Uses batch inference when multiple animal crops are present.

    Returns:
        Updated detections list and warning messages for the UI.
    """
    warnings: list[str] = []

    try:
        classifier = get_classifier()
    except RuntimeError as exc:
        return detections, [str(exc)]

    animal_detections = [
        d for d in detections if d.category_id == ANIMAL_CATEGORY_ID
    ]
    if not animal_detections:
        return detections, warnings

    stubs = [f"{filename}#detection_{d.detection_id}" for d in animal_detections]
    preprocessed = []
    preprocess_failures = 0

    for detection in animal_detections:
        try:
            preprocessed.append(_preprocess_for_detection(image, detection))
        except Exception:
            preprocess_failures += 1
            logger.exception(
                "Species preprocess failed for detection %s",
                detection.detection_id,
            )
            preprocessed.append(None)

    if preprocess_failures:
        warnings.append(
            f"Species preprocessing failed for {preprocess_failures} animal crop(s)."
        )

    try:
        results = classifier.batch_predict(stubs, preprocessed)
    except Exception:
        logger.exception("SpeciesNet batch_predict failed")
        warnings.append(
            "Species classification failed during inference. "
            "Detection results are still available."
        )
        return detections, warnings

    for detection, result in zip(animal_detections, results, strict=False):
        detection.species = parse_species_result(result, species_min_confidence)

    classified = sum(1 for d in animal_detections if d.species)
    if classified == 0:
        warnings.append(
            "Species classification was enabled but no species predictions were returned. "
            "Try again after SpeciesNet model weights finish downloading."
        )

    borderline = sum(
        1
        for d in animal_detections
        if d.species and d.species.confidence_tier == SPECIES_TIER_BORDERLINE
    )
    if borderline:
        warnings.append(
            f"{borderline} animal detection(s) have borderline species confidence — "
            "review alternatives in the results table."
        )

    uncertain = sum(
        1
        for d in animal_detections
        if d.species and d.species.confidence_tier == SPECIES_TIER_UNCERTAIN
    )
    if uncertain:
        warnings.append(
            f"{uncertain} animal detection(s) had low species confidence "
            f"(below {species_min_confidence:.2f}) and were marked Uncertain."
        )

    return detections, warnings


__all__ = [
    "DEFAULT_SPECIES_MIN_CONFIDENCE",
    "UNCERTAIN_LABEL",
    "apply_species_confidence_tier",
    "enrich_with_species",
    "get_classifier",
    "parse_species_result",
]
