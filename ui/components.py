"""BioDex Gradio UI HTML and dataframe helpers."""

from __future__ import annotations

import base64
import json
import urllib.request
from pathlib import Path
from typing import Any, cast

import pandas as pd
from core.types import (
    ANIMAL_CATEGORY_ID,
    BIODEX_VERSION,
    AnalysisResult,
    BatchResult,
    DetectionRecord,
    format_species_alternatives,
    format_species_display,
)
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "examples"
MANIFEST_PATH = EXAMPLES_DIR / "manifest.json"
FAVICON_PATH = Path(__file__).resolve().parent / "favicon.png"


def _favicon_data_uri() -> str:
    if not FAVICON_PATH.is_file():
        return ""
    try:
        encoded = base64.b64encode(FAVICON_PATH.read_bytes()).decode("ascii")
    except OSError:
        return ""
    return f"data:image/png;base64,{encoded}"

_MEGA_BASE = "https://raw.githubusercontent.com/agentmorris/MegaDetector/main/images"

SAMPLE_URLS = {
    "sample.jpg": f"{_MEGA_BASE}/orinoquia-thumb-web.jpg",
    "channel_islands.jpg": f"{_MEGA_BASE}/channel-islands-thumb.jpg",
    "idaho.jpg": f"{_MEGA_BASE}/idaho-camera-traps.jpg",
    "nacti.jpg": f"{_MEGA_BASE}/nacti.jpg",
    "pheasant.jpg": f"{_MEGA_BASE}/pheasant_web.jpg",
    "timelapse.jpg": f"{_MEGA_BASE}/recognitionInTimelapse.jpg",
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

FIELD_TABLE_COLUMNS = ["File", "Animals", "Species", "Status"]

FIELD_DETECTION_COLUMNS = ["Category", "Species", "Det. conf"]


def load_manifest() -> dict[str, Any]:
    """Load examples/manifest.json if present."""
    if not MANIFEST_PATH.exists():
        return {"samples": [], "default_sample_id": None}
    return cast(dict[str, Any], json.loads(MANIFEST_PATH.read_text(encoding="utf-8")))


def get_default_sample() -> dict[str, Any] | None:
    """Return the default sample entry from the manifest."""
    manifest = load_manifest()
    default_id = manifest.get("default_sample_id")
    for sample in manifest.get("samples", []):
        if sample.get("id") == default_id:
            return cast(dict[str, Any], sample)
    samples = manifest.get("samples", [])
    return cast(dict[str, Any], samples[0]) if samples else None


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

    path = EXAMPLES_DIR / str(sample["file"])
    if path.exists():
        return path

    url = SAMPLE_URLS.get(str(sample["file"]))
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
    return ""


def header_html() -> str:
    """Minimal field-review header."""
    icon_uri = _favicon_data_uri()
    icon_markup = (
        f'<img src="{icon_uri}" alt="" />'
        if icon_uri
        else ""
    )
    return f"""
    <div class="field-header">
      <div class="field-header-main">
        <span class="field-title-main">
          <span class="field-title-icon" aria-hidden="true">{icon_markup}</span>
          BioDex Field Review
        </span>
        <span class="field-version">v{BIODEX_VERSION}</span>
      </div>
      <div class="field-header-rule" aria-hidden="true"></div>
    </div>
    """


def welcome_html() -> str:
    return ""


def footer_tagline_html() -> str:
    return """
    <div class="field-footer-tagline">
        <span class="field-footer-badge">
          <span class="field-footer-badge-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none"><path d="M4 7h3l2-3h6l2 3h3a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2Z"
              stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="13" r="3" stroke="currentColor" stroke-width="1.5"/></svg>
          </span>
          Trail camera triage
        </span>
        <span class="field-footer-badge">
          <span class="field-footer-badge-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none"><path d="M12 3 4 7v6c0 5 3.5 8.5 8 10 4.5-1.5 8-5 8-10V7l-8-4Z"
              stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="m9 12 2 2 4-4"
              stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
          </span>
          Local only
        </span>
        <span class="field-footer-badge">
          <span class="field-footer-badge-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none"><path d="M18 10h-1.26A8 8 0 1 0 9 18"
              stroke="currentColor" stroke-width="1.5"/><path d="M16 16 22 22M22 16l-6 6"
              stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
          </span>
          No cloud upload
        </span>
    </div>
    """


def footer_chips_html() -> str:
    return """
    <div class="field-footer-chips">
        <a class="field-footer-chip" href="https://gradio.app" target="_blank"
          rel="noopener noreferrer">
          <span class="field-footer-chip-icon field-footer-chip-icon-gradio" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none"><path d="M7 16 12 19l5-3M7 10l5 3 5-3M7 4l5 3 5-3"
              stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>
          </span>
          Built with Gradio
        </a>
        <button type="button" class="field-footer-chip"
          onclick="document.querySelector('#settings-tab-button, button[aria-label=\\'Settings\\']')?.click()">
          <span class="field-footer-chip-icon field-footer-chip-icon-settings" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="3"
              stroke="currentColor" stroke-width="1.5"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"
              stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
          </span>
          Settings
        </button>
    </div>
    """


def footer_html() -> str:
    return f'<div class="field-footer">{footer_tagline_html()}{footer_chips_html()}</div>'


def _species_status_html(level: str, message: str) -> str:
    """Compact status pill for SpeciesNet readiness."""
    return (
        f'<div class="field-species-pill field-species-{level}">'
        f'<span class="field-species-pill-label">{message}</span></div>'
    )


SPECIES_STATUS_INITIAL = _species_status_html(
    "loading",
    "SpeciesNet loads on first Process Folder run.",
)


def probe_speciesnet(*, active: bool) -> str:
    """
    Check whether SpeciesNet can run and return a friendly HTML status line.

    Does not load the model — that happens during Process Folder.
    """
    if not active:
        return _species_status_html(
            "off",
            "Species off — animals detected, no species labels.",
        )
    try:
        import speciesnet  # noqa: F401
    except ImportError:
        return _species_status_html(
            "error",
            "SpeciesNet not installed — run: pip install \"biodex[heavy]\" --prefer-binary",
        )
    try:
        from core.classifier import is_classifier_loaded

        if is_classifier_loaded():
            return _species_status_html(
                "ok",
                "SpeciesNet ready — labels appear on annotations and detection tables.",
            )
        return _species_status_html(
            "loading",
            "SpeciesNet loads on first Process Folder run.",
        )
    except RuntimeError as exc:
        message = str(exc)
        lower = message.lower()
        if any(token in lower for token in ("download", "weights", "first run", "214 mb")):
            return _species_status_html(
                "loading",
                "First run — downloading SpeciesNet weights (~214 MB). Keep this tab open.",
            )
        short = message.split("Details:")[0].strip().rstrip(".")
        return _species_status_html("warn", short or "SpeciesNet could not load.")
    except Exception as exc:
        return _species_status_html("warn", f"SpeciesNet check failed: {exc}")


def batch_species_status_html(batch: BatchResult) -> str:
    """Post-batch species summary for the status pill."""
    if not batch.species_enabled:
        return probe_speciesnet(active=False)

    if batch.species_counts:
        ranked = sorted(batch.species_counts.items(), key=lambda item: item[1], reverse=True)[:3]
        summary = ", ".join(f"{name} ({count})" for name, count in ranked)
        return _species_status_html("ok", f"Species IDs applied — top: {summary}")

    warnings: list[str] = []
    for result in batch.results:
        warnings.extend(result.warnings)
        if result.species_warning:
            warnings.append(result.species_warning)

    if warnings:
        return _species_status_html("warn", warnings[0])

    if batch.animal_count:
        return _species_status_html(
            "warn",
            "Species enabled but no labels returned — weights may still be downloading.",
        )
    return probe_speciesnet(active=True)


def format_field_batch_summary(batch: BatchResult) -> str:
    """Tight aggregate panel aligned with batch_report.txt."""
    blank_rate = (batch.blank_count / batch.total_images * 100) if batch.total_images else 0.0
    multi_animal = sum(1 for result in batch.results if result.animal_count >= 2)
    top_species = ""
    if batch.species_counts:
        ranked = sorted(batch.species_counts.items(), key=lambda item: item[1], reverse=True)[:4]
        top_species = ", ".join(f"{name} ({count})" for name, count in ranked)
    elif batch.species_enabled and batch.animal_count:
        top_species = "No IDs"

    species_row = (
        f'<div class="field-stat field-stat-species"><span class="field-stat-val">{top_species or "—"}</span>'
        f'<span class="field-stat-lbl">Top species</span></div>'
        if batch.species_enabled
        else ""
    )

    return f"""
<div class="field-summary field-summary-active">
  <div class="field-stat field-stat-primary"><span class="field-stat-val">{batch.total_images}</span><span class="field-stat-lbl">Images</span></div>
  <div class="field-stat field-stat-animal field-stat-primary"><span class="field-stat-val">{batch.animal_count}</span><span class="field-stat-lbl">Animals</span></div>
  <div class="field-stat field-stat-primary"><span class="field-stat-val">{multi_animal}</span><span class="field-stat-lbl">Multi-animal</span></div>
  <div class="field-stat"><span class="field-stat-val">{blank_rate:.0f}%</span><span class="field-stat-lbl">Blanks</span></div>
  <div class="field-stat"><span class="field-stat-val">{batch.total_detections}</span><span class="field-stat-lbl">Detections</span></div>
  <div class="field-stat"><span class="field-stat-val">{len(batch.failed)}</span><span class="field-stat-lbl">Failed</span></div>
  {species_row}
</div>
"""


def build_field_batch_dataframe(batch: BatchResult) -> pd.DataFrame:
    """Minimal per-image table for field review."""
    rows = []
    for result in batch.results:
        if result.species_enabled:
            species_cell = _top_species_for_result(result) or ("—" if result.animal_count else "—")
        else:
            species_cell = "off"
        rows.append(
            [
                result.filename,
                result.animal_count,
                species_cell,
                "Failed" if result.error else ("Blank" if result.is_blank else "OK"),
            ]
        )
    return pd.DataFrame(rows, columns=FIELD_TABLE_COLUMNS)


def _species_cell_for_detection(
    detection: DetectionRecord,
    *,
    species_enabled: bool,
) -> str:
    """Format species column for one detection row."""
    if detection.category_id != ANIMAL_CATEGORY_ID:
        return "—"
    if not species_enabled:
        return "off"
    if detection.species:
        display = format_species_display(detection.species)
        return display or detection.species.label or "—"
    return "No match"


def build_minimal_detections_dataframe(result: AnalysisResult) -> pd.DataFrame:
    """Per-frame detection rows for the review panel."""
    rows = []
    for detection in result.detections:
        rows.append(
            [
                detection.category.title(),
                _species_cell_for_detection(
                    detection,
                    species_enabled=result.species_enabled,
                ),
                f"{detection.confidence:.2f}",
            ]
        )
    return pd.DataFrame(rows, columns=FIELD_DETECTION_COLUMNS)


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
