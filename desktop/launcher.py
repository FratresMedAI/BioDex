"""
BioDex desktop entry point.

Double-click (or run BioDex.exe) to start the field-review UI locally.
Opens your default browser to http://127.0.0.1:7860 — no terminal required
when built with console=False.

Model weights (~500 MB) download once on first analysis to your user folder.
"""

from __future__ import annotations

import logging
import os
import sys
import threading
import traceback
import webbrowser
from pathlib import Path

_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def log_file_path(data_dir: Path) -> Path:
    """Return the desktop log file path under the BioDex data directory."""
    return data_dir / "biodex.log"


def configure_data_dirs(data_dir: Path) -> None:
    """Set per-user model and cache environment variables."""
    data_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("TORCH_HOME", str(data_dir / "torch"))
    os.environ.setdefault("XDG_CACHE_HOME", str(data_dir / "cache"))


def _setup_logging(data_dir: Path) -> logging.Logger:
    """Configure file logging for windowed desktop launches."""
    log_path = log_file_path(data_dir)
    logger = logging.getLogger("biodex.desktop")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        logger.addHandler(handler)
    return logger


def _configure_runtime() -> tuple[Path, logging.Logger]:
    """Set paths for PyInstaller bundles and per-user model/cache data."""
    if getattr(sys, "frozen", False):
        bundle = Path(getattr(sys, "_MEIPASS", Path.cwd()))
        os.chdir(bundle)
        root = str(bundle)
        if root not in sys.path:
            sys.path.insert(0, root)

    data_dir = Path(os.environ.get("BIODEX_DATA_DIR", Path.home() / "BioDex"))
    configure_data_dirs(data_dir)
    logger = _setup_logging(data_dir)
    logger.info("BioDex desktop runtime configured (data_dir=%s)", data_dir)
    return data_dir, logger


def _browser_url(host: str, port: int) -> str:
    if host in {"0.0.0.0", "::"}:
        return f"http://127.0.0.1:{port}"
    return f"http://{host}:{port}"


def _open_browser_when_ready(host: str, port: int, delay: float = 2.5) -> None:
    if os.environ.get("BIODEX_NO_BROWSER", "").strip().lower() in {"1", "true", "yes"}:
        return
    url = _browser_url(host, port)
    threading.Timer(delay, lambda: webbrowser.open(url)).start()


def main() -> None:
    """Launch BioDex field-review UI for desktop use."""
    data_dir, logger = _configure_runtime()
    os.environ.setdefault("BIODEX_HOST", "127.0.0.1")
    os.environ.setdefault("BIODEX_PORT", "7860")
    os.environ.setdefault("BIODEX_ENABLE_QUEUE", "1")

    host = os.environ["BIODEX_HOST"]
    port = int(os.environ["BIODEX_PORT"])
    logger.info("Starting BioDex UI at http://%s:%s", host, port)
    logger.info(
        "First analysis downloads model weights (~500 MB) to %s; keep network on.",
        data_dir,
    )
    _open_browser_when_ready(host, port)

    try:
        from app import launch_app

        launch_app()
    except Exception:
        logger.exception("BioDex failed to start")
        log_path = log_file_path(data_dir)
        try:
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write("\n--- startup failure ---\n")
                handle.write(traceback.format_exc())
        except OSError:
            pass
        raise


if __name__ == "__main__":
    main()
