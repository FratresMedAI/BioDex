"""Persist UI preferences to ~/.cache/biodex/settings.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SETTINGS_PATH = Path.home() / ".cache" / "biodex" / "settings.json"

DEFAULTS: dict[str, Any] = {
    "threshold": 0.25,
    "classify_species": True,
    "dark_mode": False,
    "geofence_region": "",
    "detector_id": "MDV5A",
    "api_key": "",
    "llm_provider": "openai",
    "llm_model": "gpt-5.5",
    "llm_base_url": "http://localhost:11434/v1",
}


def load_settings() -> dict[str, Any]:
    """Load persisted settings; return defaults when file missing."""
    if not SETTINGS_PATH.is_file():
        return dict(DEFAULTS)
    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        merged = dict(DEFAULTS)
        merged.update(data)
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULTS)


def save_settings(**kwargs: Any) -> dict[str, Any]:
    """Merge and persist settings."""
    current = load_settings()
    current.update({k: v for k, v in kwargs.items() if k in DEFAULTS})
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps(current, indent=2), encoding="utf-8")
    return current


__all__ = ["DEFAULTS", "SETTINGS_PATH", "load_settings", "save_settings"]
