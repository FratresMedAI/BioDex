"""Desktop launcher helpers."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

from desktop.launcher import (
    _browser_url,
    configure_data_dirs,
    log_file_path,
)


def test_browser_url_localhost() -> None:
    assert _browser_url("127.0.0.1", 7860) == "http://127.0.0.1:7860"


def test_browser_url_bind_all() -> None:
    assert _browser_url("0.0.0.0", 7860) == "http://127.0.0.1:7860"


def test_log_file_path_under_data_dir(tmp_path: Path) -> None:
    data_dir = tmp_path / "BioDex"
    assert log_file_path(data_dir) == data_dir / "biodex.log"


def test_configure_data_dirs_sets_cache_env(tmp_path: Path) -> None:
    data_dir = tmp_path / "userdata"
    with patch.dict(os.environ, {}, clear=True):
        configure_data_dirs(data_dir)
        assert os.environ["TORCH_HOME"] == str(data_dir / "torch")
        assert os.environ["XDG_CACHE_HOME"] == str(data_dir / "cache")


def test_frozen_bundle_inserts_meipass_on_path(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    fake_launcher = bundle / "launcher.py"
    fake_launcher.write_text("x", encoding="utf-8")
    original_path = list(sys.path)
    original_frozen = getattr(sys, "frozen", False)
    original_meipass = getattr(sys, "_MEIPASS", None)
    try:
        sys.frozen = True  # type: ignore[attr-defined]
        sys._MEIPASS = str(bundle)  # type: ignore[attr-defined]
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("desktop.launcher.Path.home", return_value=tmp_path),
        ):
            from desktop import launcher

            launcher._configure_runtime()
        assert str(bundle) in sys.path
    finally:
        sys.path[:] = original_path
        if original_meipass is None:
            delattr(sys, "_MEIPASS")
        else:
            sys._MEIPASS = original_meipass  # type: ignore[attr-defined]
        if not original_frozen:
            delattr(sys, "frozen")
