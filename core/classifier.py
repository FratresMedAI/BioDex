"""
SpeciesNet species classification for BioDex animal detections (facade).

Loads SpeciesNet lazily on first use when species classification is enabled.
"""

from __future__ import annotations

import logging
from typing import Any

from PIL import Image

from core.config import get_model_settings
from core.models.registry import get_classifier as _registry_get_classifier
from core.models.speciesnet import (
    DEFAULT_CLASSIFIER_ID,
    apply_species_confidence_tier,
    parse_species_result,
)
from core.types import (
    DEFAULT_SPECIES_MIN_CONFIDENCE,
    UNCERTAIN_LABEL,
    DetectionRecord,
)

logger = logging.getLogger(__name__)


def is_classifier_loaded() -> bool:
    """Return True when SpeciesNet has been loaded in this process."""
    try:
        return _registry_get_classifier().is_loaded
    except ValueError:
        return False


def get_classifier() -> Any:
    """
    Return a cached SpeciesNetClassifier instance.

    Raises RuntimeError if the classifier failed to load on a prior attempt.
    """
    adapter = _registry_get_classifier()
    adapter.load()
    return getattr(adapter, "_classifier", adapter)


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
    settings = get_model_settings()
    adapter = _registry_get_classifier()
    return adapter.enrich(
        image,
        detections,
        filename,
        species_min_confidence=species_min_confidence,
        geofence_region=settings.geofence_region,
    )


__all__ = [
    "DEFAULT_CLASSIFIER_ID",
    "DEFAULT_SPECIES_MIN_CONFIDENCE",
    "UNCERTAIN_LABEL",
    "apply_species_confidence_tier",
    "enrich_with_species",
    "get_classifier",
    "is_classifier_loaded",
    "parse_species_result",
]
