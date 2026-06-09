"""Console entry point for the BioDex Gradio UI."""

from __future__ import annotations

import os


def main() -> None:
    """Launch the Gradio web application."""
    # Force a non-interactive matplotlib backend before anything imports it.
    # Gradio runs handlers in worker threads; a GUI backend (e.g. TkAgg) blocks
    # there, leaving analytics charts stuck in a "processing" state on Windows.
    os.environ.setdefault("MPLBACKEND", "Agg")

    from core.ui_app import launch_app

    launch_app()


if __name__ == "__main__":
    main()

__all__ = ["main"]
