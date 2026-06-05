"""
BioDex limited public demo — Hugging Face Spaces entry.

Restrictions (enforced in demo/limits.py, not in core UI):
  - Max 30 images per batch
  - No annotated ZIP export
  - Prominent banner directing users to run locally from GitHub
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Local dev: repo root on path when running from a full checkout.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if _REPO_ROOT.is_dir() and str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

os.environ.setdefault("BIODEX_DEPLOY", "1")
os.environ.setdefault("BIODEX_HOST", "0.0.0.0")
os.environ.setdefault("BIODEX_ENABLE_QUEUE", "1")
os.environ.setdefault("BIODEX_DEFAULT_CLASSIFY_SPECIES", "1")

try:
    from demo.limits import DEMO_EXTRA_CSS, apply_demo_patches  # noqa: E402
except ImportError:
    from limits import DEMO_EXTRA_CSS, apply_demo_patches  # type: ignore[import-not-found]  # noqa: E402

from app import build_app  # noqa: E402
from core.config import get_settings  # noqa: E402
from ui.styles import APP_THEME, CUSTOM_CSS  # noqa: E402


def launch_demo() -> None:
    """Build and launch the restricted public demo."""
    apply_demo_patches()
    settings = get_settings()
    demo_app = build_app()
    if settings.enable_queue:
        demo_app.queue(default_concurrency_limit=2)
    demo_app.launch(
        server_name=settings.host,
        server_port=settings.port,
        theme=APP_THEME,
        css=CUSTOM_CSS + DEMO_EXTRA_CSS,
        auth=settings.gradio_auth,
        show_error=True,
    )


if __name__ == "__main__":
    launch_demo()
