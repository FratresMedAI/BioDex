"""BioDex Gradio UI HTML and dataframe helpers."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import pandas as pd
from PIL import Image

from core.types import (
    BIODEX_VERSION,
    AnalysisResult,
    BatchResult,
    format_species_alternatives,
    format_species_display,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "examples"
MANIFEST_PATH = EXAMPLES_DIR / "manifest.json"

SAMPLE_URLS = {
    "sample.jpg": (
        "https://github.com/agentmorris/MegaDetector/raw/main/images/orinoquia-thumb-web.jpg"
    ),
}

RESULTS_COLUMNS = [
    "ID",
    "Category",
    "Confidence",
    "Species",
    "Species Conf",
    "Tier",
    "Alternatives",
    "BBox",
]

BATCH_COLUMNS = [
    "Filename",
    "Total",
    "Animals",
    "People",
    "Vehicles",
    "Blank",
    "Top Species",
    "Status",
]


def load_manifest() -> dict:
    """Load examples/manifest.json if present."""
    if not MANIFEST_PATH.exists():
        return {"samples": [], "default_sample_id": None}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def get_default_sample() -> dict | None:
    """Return the default sample entry from the manifest."""
    manifest = load_manifest()
    default_id = manifest.get("default_sample_id")
    for sample in manifest.get("samples", []):
        if sample.get("id") == default_id:
            return sample
    samples = manifest.get("samples", [])
    return samples[0] if samples else None


def ensure_sample_image() -> Path:
    """
    Ensure the default demo sample exists, downloading it if necessary.

    Returns:
        Path to the sample image file.

    Raises:
        FileNotFoundError: If the sample cannot be resolved or downloaded.
    """
    sample = get_default_sample()
    if not sample:
        raise FileNotFoundError(
            "No demo sample configured. Run: python scripts/fetch_examples.py"
        )

    path = EXAMPLES_DIR / sample["file"]
    if path.exists():
        return path

    url = SAMPLE_URLS.get(sample["file"])
    if not url:
        raise FileNotFoundError(
            f"Demo sample missing at {path} and no download URL is configured. "
            "Run: python scripts/fetch_examples.py"
        )

    EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve(url, path)
    except Exception as exc:
        raise FileNotFoundError(
            f"Could not download demo sample to {path}: {exc}"
        ) from exc

    return path


def load_sample_image() -> tuple[Image.Image, str]:
    """
    Load the default bundled sample image.

    Returns:
        PIL image and a short description for the UI.
    """
    sample = get_default_sample()
    if not sample:
        raise FileNotFoundError(
            "No sample images configured. Run: python scripts/fetch_examples.py"
        )

    path = ensure_sample_image()
    title = sample.get("title", sample["file"])
    description = sample.get("description", "")
    note = f"Loaded: {title}. {description}".strip()
    return Image.open(path), note


def demo_tab_intro_html() -> str:
    """Render the Demo Mode introduction panel."""
    sample = get_default_sample()
    title = sample.get("title", "camera trap sample") if sample else "camera trap sample"
    description = (
        sample.get("description", "Detection and species classification demo.")
        if sample
        else "Detection and species classification demo."
    )
    return f"""
    <div class="biodex-demo-hero">
      <p>
        One-click walkthrough on the bundled <strong>{title}</strong> image —
        detection, species classification, and export, entirely on your machine.
      </p>
      <p class="biodex-demo-detail">{description}</p>
      <span class="biodex-demo-callout">Expected: 1 animal · Ocelot · high confidence</span>
    </div>
    """


def header_html() -> str:
    """Render the BioDex page header."""
    return f"""
    <div class="biodex-shell">
      <div class="biodex-header">
        <h1><span class="biodex-title-accent">BioDex</span> — Wildlife Camera Trap Analysis</h1>
        <p class="biodex-tagline">
          Detect wildlife, filter blanks, identify species, and export field-ready results —
          privately, on your own computer.
        </p>
        <div class="biodex-badge-row">
          <span class="biodex-badge biodex-badge-version">v{BIODEX_VERSION}</span>
          <span class="biodex-badge biodex-badge-privacy">Local only · Privacy-first</span>
        </div>
      </div>
    </div>
    """


def welcome_html() -> str:
    """Render the compact onboarding panel."""
    return """
    <div class="biodex-welcome">
      <h3>Get started</h3>
      <ol class="biodex-welcome-steps">
        <li class="biodex-welcome-step">
          <span class="biodex-welcome-step-num">1.</span>
          Click <strong>Run Demo</strong> in the featured section below.
        </li>
        <li class="biodex-welcome-step">
          <span class="biodex-welcome-step-num">2.</span>
          Or upload images under <strong>Single Image</strong> or <strong>Batch Folder</strong>.
        </li>
        <li class="biodex-welcome-step">
          <span class="biodex-welcome-step-num">3.</span>
          Export annotated PNG, CSV, JSON, or a ZIP bundle when ready.
        </li>
      </ol>
    </div>
    """


def footer_html() -> str:
    return """
    <div class="biodex-footer">
        Local only &nbsp;•&nbsp; Privacy-first &nbsp;•&nbsp; Open source
    </div>
    """


def _format_bbox(bbox: list[float]) -> str:
    xmin, ymin, width, height = bbox
    return f"{xmin:.3f},{ymin:.3f},{width:.3f},{height:.3f}"


def format_warnings_html(warnings: list[str]) -> str:
    if not warnings:
        return ""
    items = "".join(f"<li>{w}</li>" for w in warnings)
    return f'<div class="biodex-warning"><strong>Notes</strong><ul>{items}</ul></div>'


def format_stats_html(result: AnalysisResult) -> str:
    blank_label = "Yes" if result.is_blank else "No"
    warnings_html = format_warnings_html(result.warnings)
    return f"""
{warnings_html}
<div class="biodex-stat-grid">
  <div class="biodex-stat biodex-stat-total">
    <div class="biodex-stat-value">{result.total}</div>
    <div class="biodex-stat-label">Total detections</div>
  </div>
  <div class="biodex-stat biodex-stat-animal">
    <div class="biodex-stat-value">{result.animal_count}</div>
    <div class="biodex-stat-label">Animals</div>
  </div>
  <div class="biodex-stat biodex-stat-person">
    <div class="biodex-stat-value">{result.person_count}</div>
    <div class="biodex-stat-label">People</div>
  </div>
  <div class="biodex-stat biodex-stat-vehicle">
    <div class="biodex-stat-value">{result.vehicle_count}</div>
    <div class="biodex-stat-label">Vehicles</div>
  </div>
  <div class="biodex-stat biodex-stat-blank">
    <div class="biodex-stat-value">{blank_label}</div>
    <div class="biodex-stat-label">Blank image</div>
  </div>
</div>
<div class="biodex-summary">{result.summary}</div>
"""


def build_results_dataframe(result: AnalysisResult) -> pd.DataFrame:
    rows = []
    for detection in result.detections:
        species_label = detection.species.label if detection.species else ""
        species_conf = (
            f"{detection.species.confidence:.3f}" if detection.species else ""
        )
        tier = detection.species.confidence_tier if detection.species else ""
        alternatives = format_species_alternatives(detection.species)
        rows.append(
            [
                detection.detection_id,
                detection.category.title(),
                f"{detection.confidence:.3f}",
                species_label,
                species_conf,
                tier,
                alternatives,
                _format_bbox(detection.bbox),
            ]
        )
    return pd.DataFrame(rows, columns=RESULTS_COLUMNS)


def _top_species_for_result(result: AnalysisResult) -> str:
    best = None
    for detection in result.detections:
        if detection.species and (
            best is None or detection.species.confidence > best.confidence
        ):
            best = detection.species
    if not best:
        return ""
    return format_species_display(best)


def build_batch_dataframe(batch: BatchResult) -> pd.DataFrame:
    rows = []
    for result in batch.results:
        rows.append(
            [
                result.filename,
                result.total,
                result.animal_count,
                result.person_count,
                result.vehicle_count,
                "Yes" if result.is_blank else "No",
                _top_species_for_result(result),
                "Failed" if result.error else "OK",
            ]
        )
    return pd.DataFrame(rows, columns=BATCH_COLUMNS)


def format_batch_stats_html(batch: BatchResult) -> str:
    failed_note = ""
    if batch.failed:
        failed_note = format_warnings_html(
            [f"{name}: {err}" for name, err in batch.failed]
        )

    species_lines = ""
    if batch.species_counts:
        top_species = list(batch.species_counts.items())[:5]
        species_text = ", ".join(f"{label} ({count})" for label, count in top_species)
        species_lines = f'<div class="biodex-summary">Top species: {species_text}</div>'

    return f"""
{failed_note}
<div class="biodex-stat-grid">
  <div class="biodex-stat biodex-stat-total">
    <div class="biodex-stat-value">{batch.total_images}</div>
    <div class="biodex-stat-label">Images</div>
  </div>
  <div class="biodex-stat biodex-stat-blank">
    <div class="biodex-stat-value">{batch.blank_count}</div>
    <div class="biodex-stat-label">Blanks</div>
  </div>
  <div class="biodex-stat biodex-stat-total">
    <div class="biodex-stat-value">{batch.total_detections}</div>
    <div class="biodex-stat-label">Total detections</div>
  </div>
  <div class="biodex-stat biodex-stat-animal">
    <div class="biodex-stat-value">{batch.animal_count}</div>
    <div class="biodex-stat-label">Animals</div>
  </div>
  <div class="biodex-stat biodex-stat-person">
    <div class="biodex-stat-value">{len(batch.failed)}</div>
    <div class="biodex-stat-label">Failed</div>
  </div>
</div>
{species_lines}
"""
