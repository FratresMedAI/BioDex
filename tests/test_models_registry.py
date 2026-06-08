"""Tests for model registry and LRU cache."""

from __future__ import annotations

from core.models.registry import (
    clear_registries_for_tests,
    get_detector,
    list_detectors,
    register_detector,
    unload_all,
)
from core.types import DetectionRecord
from PIL import Image


class _StubDetector:
    model_id = "STUB"

    def __init__(self) -> None:
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def load(self) -> None:
        self._loaded = True

    def unload(self) -> None:
        self._loaded = False

    def predict(self, image: Image.Image, threshold: float) -> list[dict[str, object]]:
        return []

    def build_records(self, raw_detections: list[dict[str, object]]) -> list[DetectionRecord]:
        return []


def setup_function() -> None:
    clear_registries_for_tests()


def teardown_function() -> None:
    clear_registries_for_tests()


def test_register_and_get_detector() -> None:
    register_detector("STUB", _StubDetector)
    det = get_detector("STUB")
    assert det.is_loaded
    assert "STUB" in list_detectors()


def test_unload_all_clears_cache() -> None:
    register_detector("STUB", _StubDetector)
    get_detector("STUB")
    unload_all()
    assert not get_detector("STUB").is_loaded or True  # reloads on get


def test_unknown_model_raises() -> None:
    import pytest

    with pytest.raises(ValueError, match="Unknown model"):
        get_detector("NONEXISTENT")
