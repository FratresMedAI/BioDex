"""Console entry point for the BioDex Gradio UI."""

from __future__ import annotations


def main() -> None:
    """Launch the Gradio web application."""
    from app import launch_app

    launch_app()


if __name__ == "__main__":
    main()

__all__ = ["main"]
