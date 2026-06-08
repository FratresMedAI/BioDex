"""Pluggable model registry — public exports and default registrations."""

from __future__ import annotations

from core.models.base import BaseClassifier, BaseDetector
from core.models.edge import ONNXDetectorAdapter, TensorRTDetectorAdapter
from core.models.megadetector import MegaDetectorAdapter
from core.models.registry import (
    get_classifier,
    get_detector,
    list_classifiers,
    list_detectors,
    register_classifier,
    register_detector,
    unload_all,
)
from core.models.speciesnet import DEFAULT_CLASSIFIER_ID, SpeciesNetAdapter

# Register defaults at import time.
register_detector("MDV5A", MegaDetectorAdapter)
register_classifier(DEFAULT_CLASSIFIER_ID, SpeciesNetAdapter)

__all__ = [
    "BaseClassifier",
    "BaseDetector",
    "DEFAULT_CLASSIFIER_ID",
    "MegaDetectorAdapter",
    "ONNXDetectorAdapter",
    "SpeciesNetAdapter",
    "TensorRTDetectorAdapter",
    "get_classifier",
    "get_detector",
    "list_classifiers",
    "list_detectors",
    "register_classifier",
    "register_detector",
    "unload_all",
]
