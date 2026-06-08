"""Tests for ModelSettings env parsing."""

from __future__ import annotations

import pytest
from core.config import ModelSettings


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in (
        "BIODEX_DETECTOR_MODEL",
        "BIODEX_CLASSIFIER_MODEL",
        "BIODEX_TORCH_COMPILE",
        "BIODEX_DEVICE",
        "BIODEX_GEOFENCE_REGION",
        "BIODEX_MODEL_CACHE_SIZE",
    ):
        monkeypatch.delenv(key, raising=False)


def test_model_settings_defaults() -> None:
    settings = ModelSettings.from_env()
    assert settings.detector_id == "MDV5A"
    assert settings.classifier_id == "speciesnet"
    assert settings.torch_compile is False
    assert settings.device == "auto"
    assert settings.geofence_region is None
    assert settings.cache_size == 2


def test_model_settings_torch_compile(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BIODEX_TORCH_COMPILE", "1")
    settings = ModelSettings.from_env()
    assert settings.torch_compile is True


def test_model_settings_geofence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BIODEX_GEOFENCE_REGION", "US")
    settings = ModelSettings.from_env()
    assert settings.geofence_region == "US"
