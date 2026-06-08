"""Model registry with LRU caching for detector and classifier backends."""

from __future__ import annotations

import gc
import logging
from collections import OrderedDict
from typing import Any, Protocol, TypeVar

from core.config import get_model_settings
from core.models.base import BaseClassifier, BaseDetector

logger = logging.getLogger(__name__)


class _LoadableModel(Protocol):
    def load(self) -> None: ...
    def unload(self) -> None: ...


T = TypeVar("T", bound=_LoadableModel)

_detector_registry: dict[str, type[BaseDetector]] = {}
_classifier_registry: dict[str, type[BaseClassifier]] = {}
_detector_cache: OrderedDict[str, BaseDetector] = OrderedDict()
_classifier_cache: OrderedDict[str, BaseClassifier] = OrderedDict()


def register_detector(model_id: str, cls: type[BaseDetector]) -> type[BaseDetector]:
    """Register a detector adapter class under ``model_id``."""
    _detector_registry[model_id] = cls
    return cls


def register_classifier(model_id: str, cls: type[BaseClassifier]) -> type[BaseClassifier]:
    """Register a classifier adapter class under ``model_id``."""
    _classifier_registry[model_id] = cls
    return cls


def _evict_lru(cache: OrderedDict[str, Any], max_size: int) -> None:
    while len(cache) >= max_size and cache:
        evicted_id, instance = cache.popitem(last=False)
        try:
            instance.unload()
        except Exception:
            logger.exception("Failed to unload model %s", evicted_id)


def _get_cached(
    cache: OrderedDict[str, T],
    registry: dict[str, type[T]],
    model_id: str,
    *,
    max_size: int,
) -> T:
    if model_id in cache:
        cache.move_to_end(model_id)
        return cache[model_id]

    if model_id not in registry:
        available = ", ".join(sorted(registry)) or "(none)"
        raise ValueError(f"Unknown model {model_id!r}. Registered: {available}")

    _evict_lru(cache, max_size)
    factory = registry[model_id]
    instance: T = factory()
    instance.load()
    cache[model_id] = instance
    cache.move_to_end(model_id)
    return instance


def get_detector(model_id: str | None = None) -> BaseDetector:
    """Return a cached detector instance for ``model_id`` (default from settings)."""
    settings = get_model_settings()
    resolved = model_id or settings.detector_id
    return _get_cached(
        _detector_cache,
        _detector_registry,
        resolved,
        max_size=settings.cache_size,
    )


def get_classifier(model_id: str | None = None) -> BaseClassifier:
    """Return a cached classifier instance for ``model_id`` (default from settings)."""
    settings = get_model_settings()
    resolved = model_id or settings.classifier_id
    return _get_cached(
        _classifier_cache,
        _classifier_registry,
        resolved,
        max_size=settings.cache_size,
    )


def unload_all() -> None:
    """Unload all cached models and run garbage collection."""
    for cache in (_detector_cache, _classifier_cache):
        while cache:
            _, instance = cache.popitem(last=False)
            try:
                instance.unload()
            except Exception:
                logger.exception("Error unloading model during unload_all")
    gc.collect()


def list_detectors() -> list[str]:
    """Return registered detector model IDs."""
    return sorted(_detector_registry)


def list_classifiers() -> list[str]:
    """Return registered classifier model IDs."""
    return sorted(_classifier_registry)


def clear_registries_for_tests() -> None:
    """Reset registries and caches — test helper only."""
    unload_all()
    _detector_registry.clear()
    _classifier_registry.clear()


__all__ = [
    "clear_registries_for_tests",
    "get_classifier",
    "get_detector",
    "list_classifiers",
    "list_detectors",
    "register_classifier",
    "register_detector",
    "unload_all",
]
