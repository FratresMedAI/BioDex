"""Opt-in tamper-evident audit logging (Caecator / FratresCustos prep)."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

AUDIT_LOG_PATH = Path.home() / ".cache" / "biodex" / "audit.log"


def _audit_enabled() -> bool:
    return os.getenv("BIODEX_AUDIT_LOG", "").strip().lower() in {"1", "true", "yes", "on"}


def _last_hash(path: Path) -> str:
    if not path.is_file():
        return "0" * 64
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines:
            return "0" * 64
        last = json.loads(lines[-1])
        return str(last.get("entry_hash", "0" * 64))
    except Exception:
        return "0" * 64


def append_audit_entry(event: str, payload: dict[str, Any]) -> None:
    """
    Append a hash-chained JSONL entry when ``BIODEX_AUDIT_LOG=1``.

    Each entry links to the previous via ``prev_hash`` for tamper detection stubs.
    """
    if not _audit_enabled():
        return

    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    prev_hash = _last_hash(AUDIT_LOG_PATH)
    body = {
        "ts": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "event": event,
        "payload": payload,
        "prev_hash": prev_hash,
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    entry_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    body["entry_hash"] = entry_hash

    try:
        with AUDIT_LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(body, sort_keys=True) + "\n")
    except OSError as exc:
        logger.warning("Audit log write failed: %s", exc)


__all__ = ["AUDIT_LOG_PATH", "append_audit_entry"]
