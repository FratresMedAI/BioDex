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


def _env_auth() -> tuple[tuple[str, str], ...] | None:
    user = os.getenv("BIODEX_AUTH_USER")
    password = os.getenv("BIODEX_AUTH_PASSWORD")
    if user and password:
        return ((user, password),)
    return None


@dataclass(frozen=True)
class BioDexSettings:
    """UI and pipeline defaults; override via BIODEX_* environment variables."""

    default_threshold: float
    default_classify_species: bool
    host: str
    port: int
    enable_queue: bool
    gradio_auth: tuple[tuple[str, str], ...] | None

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
