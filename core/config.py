"""BioDex runtime configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_float(key: str, default: float) -> float:
    raw = os.getenv(key)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"Invalid float for {key}={raw!r}") from exc


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_auth() -> list[tuple[str, str]] | None:
    user = os.getenv("BIODEX_AUTH_USER")
    password = os.getenv("BIODEX_AUTH_PASSWORD")
    if user and password:
        return [(user, password)]
    return None


@dataclass(frozen=True)
class BioDexSettings:
    """UI and pipeline defaults; override via BIODEX_* environment variables."""

    default_threshold: float
    default_classify_species: bool
    host: str
    port: int
    enable_queue: bool
    gradio_auth: list[tuple[str, str]] | None

    @classmethod
    def from_env(cls) -> BioDexSettings:
        deploy = _env_bool("BIODEX_DEPLOY", False)
        return cls(
            default_threshold=_env_float("BIODEX_DEFAULT_THRESHOLD", 0.25),
            default_classify_species=_env_bool("BIODEX_DEFAULT_CLASSIFY_SPECIES", False),
            host=os.getenv("BIODEX_HOST", "0.0.0.0" if deploy else "127.0.0.1"),
            port=int(os.getenv("BIODEX_PORT", "7860")),
            enable_queue=_env_bool("BIODEX_ENABLE_QUEUE", deploy),
            gradio_auth=_env_auth(),
        )


def get_settings() -> BioDexSettings:
    """Return cached settings snapshot from the current environment."""
    return BioDexSettings.from_env()


def _env_int(key: str, default: int) -> int:
    raw = os.getenv(key)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"Invalid int for {key}={raw!r}") from exc


@dataclass(frozen=True)
class ModelSettings:
    """Model pipeline settings; override via BIODEX_* environment variables."""

    detector_id: str
    classifier_id: str
    torch_compile: bool
    device: str
    geofence_region: str | None
    cache_size: int

    @classmethod
    def from_env(cls) -> ModelSettings:
        default_classifier = "speciesnet"
        return cls(
            detector_id=os.getenv("BIODEX_DETECTOR_MODEL", "MDV5A"),
            classifier_id=os.getenv("BIODEX_CLASSIFIER_MODEL", default_classifier),
            torch_compile=_env_bool("BIODEX_TORCH_COMPILE", False),
            device=os.getenv("BIODEX_DEVICE", "auto"),
            geofence_region=os.getenv("BIODEX_GEOFENCE_REGION") or None,
            cache_size=_env_int("BIODEX_MODEL_CACHE_SIZE", 2),
        )


def get_model_settings() -> ModelSettings:
    """Return model settings snapshot from the current environment."""
    return ModelSettings.from_env()
