"""Enforced limits for the public Hugging Face demo (wrapper layer only)."""

from __future__ import annotations

import json
import urllib.request
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any, TypeVar

import gradio as gr

DEMO_MAX_IMAGES = 30
GITHUB_REPO_URL = "https://github.com/FratresMedAI/BioDex"

DEMO_DIR = Path(__file__).resolve().parent
SAMPLE_IMAGES_DIR = DEMO_DIR / "sample_images"
MANIFEST_PATH = SAMPLE_IMAGES_DIR / "manifest.json"

_MEGA_BASE = "https://raw.githubusercontent.com/agentmorris/MegaDetector/main/images"
SAMPLE_URLS = {
    "sample.jpg": f"{_MEGA_BASE}/orinoquia-thumb-web.jpg",
    "channel_islands.jpg": f"{_MEGA_BASE}/channel-islands-thumb.jpg",
    "idaho.jpg": f"{_MEGA_BASE}/idaho-camera-traps.jpg",
    "nacti.jpg": f"{_MEGA_BASE}/nacti.jpg",
    "pheasant.jpg": f"{_MEGA_BASE}/pheasant_web.jpg",
    "timelapse.jpg": f"{_MEGA_BASE}/recognitionInTimelapse.jpg",
}

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}

DEMO_BANNER_HTML = f"""
<div class="biodex-demo-banner" role="alert">
  <div class="biodex-demo-banner-title">LIMITED PUBLIC DEMO — NOT THE FULL APP</div>
  <div>Max {DEMO_MAX_IMAGES} images per batch · No ZIP export · Processed on shared servers (not private).</div>
  <a href="{GITHUB_REPO_URL}" target="_blank" rel="noopener noreferrer">
    Get BioDex for real use — clone repo and run locally (free, private, unlimited)
  </a>
</div>
"""

DEMO_EXTRA_CSS = """
.biodex-demo-banner {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: #991b1b;
  color: #fff;
  padding: 14px 18px;
  margin: 0 0 14px 0;
  border: 2px solid #fca5a5;
  border-radius: 6px;
  font-size: 1rem;
  line-height: 1.5;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
}
.biodex-demo-banner-title {
  font-size: 1.1rem;
  font-weight: 800;
  letter-spacing: 0.02em;
  margin-bottom: 6px;
}
.biodex-demo-banner a {
  color: #fde68a;
  font-weight: 700;
  text-decoration: underline;
  display: inline-block;
  margin-top: 8px;
}
.field-export-row button:nth-of-type(3),
.field-export-row .gr-button:nth-child(3) {
  display: none !important;
}
"""

F = TypeVar("F", bound=Callable[..., Any])


def cap_image_paths(files: list[str] | None, max_images: int = DEMO_MAX_IMAGES) -> tuple[list[str], str]:
    """Return capped file paths and an optional truncation note."""
    if not files:
        return [], ""
    image_paths = sorted(
        path
        for path in files
        if Path(path).suffix.lower() in IMAGE_SUFFIXES
    )
    if not image_paths:
        return [], ""
    if len(image_paths) <= max_images:
        return image_paths, ""
    truncated = image_paths[:max_images]
    note = (
        f"Demo limit: processing first **{max_images}** of **{len(image_paths)}** images. "
        f"[Run BioDex locally]({GITHUB_REPO_URL}) for unlimited private batches."
    )
    return truncated, note


def demo_header_html(original_header: Callable[[], str]) -> Callable[[], str]:
    """Prepend the unavoidable demo banner to the field-review header."""

    @wraps(original_header)
    def _wrapped() -> str:
        return DEMO_BANNER_HTML + original_header()

    return _wrapped


def disable_zip_output(result: tuple[Any, ...]) -> tuple[Any, ...]:
    """Replace the annotated ZIP download slot with a disabled control."""
    items = list(result)
    if len(items) > 5:
        items[5] = gr.update(value=None, interactive=False)
    return tuple(items)


def wrap_analyze_batch(original: F) -> F:
    """Cap batch size and disable ZIP exports for the public demo."""

    @wraps(original)
    def _wrapped(
        files: list[str] | None,
        threshold: float,
        classify_species: bool,
        progress: Any = gr.Progress(),  # noqa: B008
    ) -> tuple[Any, ...]:
        capped, note = cap_image_paths(files)
        if not capped:
            raise gr.Error("Select a camera-trap folder with JPG/PNG images (demo max 30).")
        result = original(capped, threshold, classify_species, progress)
        items = list(disable_zip_output(result))
        if note and len(items) > 2 and isinstance(items[2], str):
            items[2] = f"{items[2]}\n\n{note}"
        return tuple(items)

    return _wrapped  # type: ignore[return-value]


def _download_sample(filename: str, url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, destination)


def ensure_sample_images() -> None:
    """Download bundled demo thumbnails into demo/sample_images when missing."""
    SAMPLE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    if not MANIFEST_PATH.exists():
        source_manifest = DEMO_DIR.parent / "examples" / "manifest.json"
        if source_manifest.exists():
            MANIFEST_PATH.write_text(source_manifest.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            default_manifest = {"samples": [{"file": name} for name in SAMPLE_URLS]}
            MANIFEST_PATH.write_text(json.dumps(default_manifest), encoding="utf-8")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    filenames = [
        sample.get("file")
        for sample in manifest.get("samples", [])
        if sample.get("file")
    ]
    if not filenames:
        filenames = list(SAMPLE_URLS)
    for filename in filenames:
        destination = SAMPLE_IMAGES_DIR / filename
        if destination.exists():
            continue
        url = SAMPLE_URLS.get(filename)
        if url:
            _download_sample(filename, url, destination)


def load_demo_sample_cache() -> tuple[list[str], str]:
    """Load bundled sample images for the demo 'Load LILA cache' button."""
    ensure_sample_images()
    paths: list[Path] = []
    for pattern in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
        paths.extend(SAMPLE_IMAGES_DIR.glob(pattern))
    files = sorted(str(path) for path in paths)[:DEMO_MAX_IMAGES]
    if not files:
        raise gr.Error(
            "Demo sample images missing. Restart the Space or "
            f"[run BioDex locally]({GITHUB_REPO_URL})."
        )
    return files, f"Loaded **{len(files)}** demo sample images (public demo subset)."


def wrap_load_lila_cache(original: F) -> F:
    """Serve bundled demo samples instead of a local LILA cache path."""

    @wraps(original)
    def _wrapped() -> tuple[list[str], str]:
        try:
            return load_demo_sample_cache()
        except gr.Error:
            raise
        except Exception as exc:
            raise gr.Error(f"Could not load demo samples: {exc}") from exc

    return _wrapped  # type: ignore[return-value]


def apply_demo_patches() -> None:
    """Monkeypatch BioDex UI hooks before build_app() runs."""
    import app as biodex_app
    import ui.components as components

    components.header_html = demo_header_html(components.header_html)
    biodex_app.analyze_batch = wrap_analyze_batch(biodex_app.analyze_batch)
    biodex_app.load_lila_cache = wrap_load_lila_cache(biodex_app.load_lila_cache)
