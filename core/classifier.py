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


def _preprocess_for_detection(image: Image.Image, detection: DetectionRecord):
    """Preprocess one animal detection for SpeciesNet batch inference."""
    from speciesnet.utils import BBox

    classifier = get_classifier()
    xmin, ymin, width, height = detection.bbox
    bboxes = [BBox(xmin=xmin, ymin=ymin, width=width, height=height)]
    return classifier.preprocess(image, bboxes=bboxes)


def enrich_with_species(
    image: Image.Image,
    detections: list[DetectionRecord],
    filename: str,
) -> tuple[list[DetectionRecord], str]:
    """
    Attach species predictions to animal detections in-place.

    Uses batch inference when multiple animal crops are present.

    Returns:
        Updated detections list and optional warning message.
    """
    warning = ""

    try:
        classifier = get_classifier()
    except RuntimeError as exc:
        return detections, str(exc)

    animal_detections = [
        d for d in detections if d.category_id == ANIMAL_CATEGORY_ID
    ]
    if not animal_detections:
        return detections, warning

    stubs = [f"{filename}#detection_{d.detection_id}" for d in animal_detections]
    preprocessed = []

    for detection in animal_detections:
        try:
            preprocessed.append(_preprocess_for_detection(image, detection))
        except Exception:
            logger.exception(
                "Species preprocess failed for detection %s",
                detection.detection_id,
            )
            preprocessed.append(None)

    try:
        results = classifier.batch_predict(stubs, preprocessed)
    except Exception:
        logger.exception("SpeciesNet batch_predict failed")
        return detections, (
            "Species classification failed during inference. "
            "Detection results are still available."
        )

    for detection, result in zip(animal_detections, results):
        detection.species = _parse_species_result(result)

    classified = sum(1 for d in animal_detections if d.species)
    if classified == 0:
        warning = (
            "Species classification was enabled but no species predictions were returned. "
            "Try again after SpeciesNet model weights finish downloading."
        )

    return detections, warning
