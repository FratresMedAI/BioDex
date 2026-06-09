"""
BioDex — dev entry point when running from a git clone.

``python app.py`` or ``biodex-ui`` (via ``core.ui_app``).
"""

from __future__ import annotations

from core.ui_app import build_app, launch_app

__all__ = ["build_app", "launch_app"]

if __name__ == "__main__":
    launch_app()
