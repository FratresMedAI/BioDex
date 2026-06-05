"""Tests for the public demo restriction wrapper."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import gradio as gr

from demo.limits import (
    DEMO_BANNER_HTML,
    DEMO_MAX_IMAGES,
    GITHUB_REPO_URL,
    cap_image_paths,
    demo_header_html,
    disable_zip_output,
    wrap_analyze_batch,
)


def test_cap_image_paths_truncates_at_limit(tmp_path: Path) -> None:
    files = [str(tmp_path / f"img_{index}.jpg") for index in range(40)]
    for path in files:
        Path(path).write_bytes(b"x")
    capped, note = cap_image_paths(files, max_images=DEMO_MAX_IMAGES)
    assert len(capped) == DEMO_MAX_IMAGES
    assert "30" in note
    assert GITHUB_REPO_URL in note


def test_cap_image_paths_keeps_small_batches(tmp_path: Path) -> None:
    files = [str(tmp_path / "a.jpg"), str(tmp_path / "b.png")]
    for path in files:
        Path(path).write_bytes(b"x")
    capped, note = cap_image_paths(files)
    assert len(capped) == 2
    assert note == ""


def test_disable_zip_output_clears_zip_slot() -> None:
    zip_update = gr.update(value="/tmp/batch.zip", interactive=True)
    result = ("a", "b", "c", "d", "e", zip_update, "g")
    patched = disable_zip_output(result)
    assert patched[5] == gr.update(value=None, interactive=False)


def test_demo_header_html_includes_banner() -> None:
    wrapped = demo_header_html(lambda: "<header>ok</header>")
    html = wrapped()
    assert "LIMITED PUBLIC DEMO" in html
    assert GITHUB_REPO_URL in html
    assert "<header>ok</header>" in html


def test_demo_banner_constant_has_github_link() -> None:
    assert GITHUB_REPO_URL in DEMO_BANNER_HTML


def test_wrap_analyze_batch_caps_and_disables_zip(tmp_path: Path) -> None:
    files = [str(tmp_path / f"frame_{index}.jpg") for index in range(5)]
    for path in files:
        Path(path).write_bytes(b"x")

    def fake_batch(
        batch_files: list[str] | None,
        threshold: float,
        classify_species: bool,
        progress: object = None,
    ) -> tuple[object, ...]:
        assert len(batch_files or []) == 5
        return (
            "stats",
            "table",
            "**Status:** done",
            gr.update(value="/tmp/out.csv", interactive=True),
            gr.update(value="/tmp/out.json", interactive=True),
            gr.update(value="/tmp/out.zip", interactive=True),
            [],
            None,
            None,
            "",
            "det",
        )

    wrapped = wrap_analyze_batch(fake_batch)
    result = wrapped(files, 0.25, True, progress=MagicMock())
    assert result[5] == gr.update(value=None, interactive=False)
