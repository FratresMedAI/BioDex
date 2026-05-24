"""
SpeciesNet species classification for BioDex animal detections.

Loads SpeciesNet lazily on first use when species classification is enabled.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from core.types import (
    ANIMAL_CATEGORY_ID,
    DetectionRecord,
    SpeciesPrediction,
    format_taxon_label,
)

if TYPE_CHECKING:
    from PIL import Image

logger = logging.getLogger(__name__)

_classifier = None
_classifier_error: str | None = None


def get_classifier():
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

        _classifier = SpeciesNetClassifier(DEFAULT_MODEL)
        return _classifier
    except Exception as exc:
        _classifier_error = f"SpeciesNet failed to load: {exc}"
        logger.exception("SpeciesNet classifier load failed")
        raise RuntimeError(_classifier_error) from exc


def _parse_species_result(result: dict) -> SpeciesPrediction | None:
    """Extract top-3 species predictions from a SpeciesNet result dict."""
    if result.get("failures"):
        return None

    classifications = result.get("classifications", {})
    classes = classifications.get("classes") or []
    scores = classifications.get("scores") or []

    if not classes or not scores:
        return None

    top3: list[tuple[str, float]] = []
    for raw_label, score in zip(classes[:3], scores[:3]):
        top3.append((format_taxon_label(raw_label), float(score)))

    best_label, best_score = top3[0]
    return SpeciesPrediction(label=best_label, confidence=best_score, top3=top3)


def classify_detection(
    image: Image.Image,
    detection: DetectionRecord,
    filepath_stub: str,
) -> SpeciesPrediction | None:
    """
    Run SpeciesNet on a single animal detection crop.

    Args:
        image: Full original PIL image.
        detection: Animal detection record with normalized bbox.
        filepath_stub: Identifier used by SpeciesNet for result keys.

    Returns:
        SpeciesPrediction or None if classification failed.
    """
    if detection.category_id != ANIMAL_CATEGORY_ID:
        return None

    try:
        from speciesnet.utils import BBox

        classifier = get_classifier()
        xmin, ymin, width, height = detection.bbox
        bboxes = [BBox(xmin=xmin, ymin=ymin, width=width, height=height)]

        preprocessed = classifier.preprocess(image, bboxes=bboxes)
        if preprocessed is None:
            return None

        result = classifier.predict(filepath_stub, preprocessed)
        return _parse_species_result(result)
    except Exception:
        logger.exception(
            "Species classification failed for detection %s", detection.detection_id
        )
        return None


def enrich_with_species(
    image: Image.Image,
    detections: list[DetectionRecord],
    filename: str,
) -> tuple[list[DetectionRecord], str]:
    """
    Attach species predictions to animal detections in-place.

    Returns:
        Updated detections list and optional warning message.
    """
    warning = ""

    try:
        get_classifier()
    except RuntimeError as exc:
        return detections, str(exc)

    for detection in detections:
        if detection.category_id != ANIMAL_CATEGORY_ID:
            continue

        stub = f"{filename}#detection_{detection.detection_id}"
        detection.species = classify_detection(image, detection, stub)

    classified = sum(
        1 for d in detections if d.category_id == ANIMAL_CATEGORY_ID and d.species
    )
    animal_total = sum(1 for d in detections if d.category_id == ANIMAL_CATEGORY_ID)

    if animal_total and classified == 0:
        warning = (
            "Species classification was enabled but no species predictions were returned. "
            "Try again after SpeciesNet model weights finish downloading."
        )

    return detections, warning
