"""Gradio event handlers extracted from app.py."""

from __future__ import annotations

import logging
import threading
import traceback
from collections.abc import Iterator
from pathlib import Path
from threading import Event
from typing import Any, cast

import gradio as gr
import pandas as pd
from core.batch import run_batch
from core.detector import analyze_single_image, warmup_models
from core.exports import (
    batch_to_csv,
    build_batch_annotated_zip,
    detections_to_csv,
    export_batch_json,
    export_bundle,
    export_ecosentinel,
    export_inaturalist,
    export_json,
    export_wildlife_insights,
    save_annotated_image,
)
from core.quick_demo import QUICK_DEMO_COUNT, ensure_quick_demo_paths
from core.types import AnalysisResult, BatchResult
from core.video import analyze_video, export_video_timeline, extract_frames
from core.visualization import draw_detections
from PIL import Image

from ui.components import (
    FIELD_DETECTION_COLUMNS,
    FIELD_TABLE_COLUMNS,
    batch_species_status_html,
    build_field_batch_dataframe,
    build_minimal_detections_dataframe,
    build_results_dataframe,
    format_field_batch_summary,
    format_stats_html,
    load_sample_image,
    probe_speciesnet,
)
from ui.llm_review import review_frame
from ui.llm_settings import (
    DEFAULT_LOCAL_BASE_URL,
    DEFAULT_PROVIDER,
    default_model,
    flatten_models,
    key_required,
    test_connection,
)
from ui.settings_store import load_settings, save_settings

BATCH_ANNOTATED_ZIP_LIMIT = 100
LILA_CACHE_DIR = Path.home() / ".cache" / "biodex" / "channel-islands-demo"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
logger = logging.getLogger(__name__)

EMPTY_FIELD_SUMMARY = (
    '<div class="field-summary field-summary-empty">'
    "Ready — Load LILA cache, then Process Folder"
    "</div>"
)

HOW_IT_WORKS = """
### How BioDex works

BioDex runs entirely on your computer. Your images are never uploaded to a cloud API.

**Step 1 — Detection (MegaDetector v5a)**  
Finds animals, people, and vehicles with bounding boxes and confidence scores.

**Step 2 — Species classification (optional)**  
SpeciesNet suggests likely species on animal crops. Borderline predictions show alternatives.

**Step 3 — Batch / Video**
Process folders and sample video frames locally.

**First run:** Model weights download once (~500 MB total), then analysis works offline.
"""

# Shared cancel event for batch/video runs
_cancel_event: Event | None = None


def get_cancel_event() -> Event:
    global _cancel_event
    if _cancel_event is None:
        _cancel_event = Event()
    return _cancel_event


def request_cancel() -> str:
    get_cancel_event().set()
    return "**Status:** Cancelling…"


def _reset_cancel() -> None:
    get_cancel_event().clear()


def _disabled_download() -> Any:
    return gr.update(value=None, interactive=False)


def _enabled_download(path: str | None) -> Any:
    if path:
        return gr.update(value=path, interactive=True)
    return gr.update(value=None, interactive=False)


def _format_model_error(exc: Exception) -> str:
    message = str(exc)
    lower = message.lower()
    if "megadetector" in lower or "failed to load" in lower:
        return f"**MegaDetector error:** {message}"
    if "speciesnet" in lower or "species" in lower:
        return f"**SpeciesNet error:** {message}"
    return f"**Analysis failed:** {message}"


def analyze_image(
    image: Image.Image | None,
    threshold: float,
    classify_species: bool,
    sample_note: str = "",
    progress: Any = gr.Progress(),  # noqa: B008
) -> tuple[Any, ...]:
    if image is None:
        raise gr.Error("Please upload a camera trap image (JPG or PNG) or use Demo Mode.")

    try:
        if not isinstance(image, Image.Image):
            image = Image.open(image)

        progress(0.05, desc="Preparing image…")
        status = "Starting analysis…"

        def on_progress(message: str) -> None:
            nonlocal status
            status = message
            progress(0.5, desc=message)

        result = analyze_single_image(
            image,
            threshold=threshold,
            classify_species=classify_species,
            filename="upload",
            progress_callback=on_progress,
        )
        annotated = draw_detections(image, result.detections)
        stats_html = format_stats_html(result)
        results_df = build_results_dataframe(result)

        annotated_path = save_annotated_image(annotated)
        csv_path = detections_to_csv(result)
        json_path = export_json(result)
        bundle_path = export_bundle(result, annotated)

        progress(1.0, desc="Analysis complete")
        note_html = (
            f'<div class="biodex-sample-note">{sample_note}</div>'
            if sample_note and not sample_note.startswith("<div")
            else (sample_note if sample_note else "")
        )

        return (
            image,
            annotated,
            note_html,
            stats_html,
            results_df,
            f"**Status:** {status} — complete.",
            _enabled_download(annotated_path),
            _enabled_download(csv_path),
            _enabled_download(json_path),
            _enabled_download(bundle_path),
        )
    except gr.Error:
        raise
    except (ValueError, RuntimeError, OSError) as exc:
        raise gr.Error(_format_model_error(exc)) from exc
    except Exception as exc:
        raise gr.Error(f"{_format_model_error(exc)}\n\n```\n{traceback.format_exc()}\n```") from exc


def run_demo_mode(progress: Any = gr.Progress()) -> tuple[Any, ...]:  # noqa: B008
    try:
        image, note = load_sample_image()
    except FileNotFoundError as exc:
        raise gr.Error(str(exc)) from exc
    progress(0, desc="Demo Mode: preparing sample image…")
    results = analyze_image(
        image=image,
        threshold=0.25,
        classify_species=True,
        sample_note=note,
        progress=progress,
    )
    return (gr.update(value=True),) + results


def try_demo(progress: Any = gr.Progress()) -> tuple[Any, ...]:  # noqa: B008
    return run_demo_mode(progress=progress)[1:]


def _resolve_batch_paths(
    files: list[str] | None,
    cache_paths: list[str] | None,
) -> list[Path]:
    raw: list[str] = []
    if files:
        raw = list(files)
    elif cache_paths:
        raw = list(cache_paths)
    return sorted(
        Path(file_path)
        for file_path in raw
        if Path(file_path).suffix.lower() in IMAGE_SUFFIXES
    )


def _review_panel_update(*, visible: bool) -> Any:
    return gr.update(visible=visible)


def _empty_batch_response(message: str) -> tuple[Any, ...]:
    empty_table = pd.DataFrame(columns=FIELD_TABLE_COLUMNS)
    empty_det = pd.DataFrame(columns=FIELD_DETECTION_COLUMNS)
    return (
        EMPTY_FIELD_SUMMARY,
        empty_table,
        message,
        probe_speciesnet(active=True),
        _disabled_download(),
        _disabled_download(),
        _disabled_download(),
        _disabled_download(),
        _disabled_download(),
        _disabled_download(),
        [],
        None,
        None,
        "",
        empty_det,
        _review_panel_update(visible=True),
        None,
    )


def analyze_batch(
    files: list[str] | None,
    cache_paths: list[str] | None,
    threshold: float,
    classify_species: bool,
    progress: Any = gr.Progress(),  # noqa: B008
    *,
    demo_paths: list[Path] | None = None,
    demo_mode: bool = False,
) -> Iterator[tuple[Any, ...]]:
    _reset_cancel()
    paths = demo_paths if demo_paths is not None else _resolve_batch_paths(files, cache_paths)
    if not paths:
        yield _empty_batch_response(
            "Load LILA cache or upload a folder (Folder upload & settings), then Process Folder."
        )
        return

    try:
        total_paths = len(paths)
        progress(0.0, desc="Loading MegaDetector…")
        warmup_models(species=classify_species)

        images: list[tuple[str, Image.Image]] = []
        for index, path in enumerate(paths):
            images.append((path.name, Image.open(path).convert("RGB")))
            if index % 12 == 0 or index == total_paths - 1:
                progress(0.02 * ((index + 1) / total_paths), desc=f"Reading images… {index + 1}/{total_paths}")

        def on_batch_progress(
            current: int,
            total: int,
            message: str,
            fraction: float | None = None,
        ) -> None:
            image_frac = fraction if fraction is not None else current / total
            progress(0.03 + 0.89 * image_frac, desc=message)

        batch = run_batch(
            images,
            threshold=threshold,
            classify_species=classify_species,
            progress_callback=on_batch_progress,
            cancel_event=get_cancel_event(),
        )

        path_by_name = {path.name: path for path in paths}
        review_state: list[dict[str, Any]] = []
        for result, (name, _image) in zip(batch.results, images, strict=True):
            review_state.append({"filename": name, "source_path": str(path_by_name[name]), "result": result})

        first = _first_review_frame(review_state)
        orig, ann, label, det_df = _frame_view(first)

        status = (
            f"**{batch.total_images}** images · **{batch.animal_count}** animals · "
            f"**{sum(1 for r in batch.results if r.animal_count >= 2)}** multi-animal frames"
        )
        if batch.interrupted:
            status += " · **cancelled**"
        if demo_mode:
            status += f" · *quick demo — {total_paths} frames*"
        if batch.failed:
            status += f" · **{len(batch.failed)}** failed"

        progress(0.93, desc="Writing CSV/JSON…")
        csv_path = batch_to_csv(batch)
        json_path = export_batch_json(batch)
        wi_path = export_wildlife_insights(batch)
        inat_path = export_inaturalist(batch)
        eco_path = export_ecosentinel(batch)

        yield (
            format_field_batch_summary(batch),
            build_field_batch_dataframe(batch),
            status,
            batch_species_status_html(batch),
            _enabled_download(csv_path),
            _enabled_download(json_path),
            _disabled_download(),
            _enabled_download(wi_path),
            _enabled_download(inat_path),
            _enabled_download(eco_path),
            review_state,
            orig,
            ann,
            label,
            det_df,
            _review_panel_update(visible=True),
            batch,
        )

        if not demo_mode and not batch.interrupted:
            progress(0.95, desc="Building annotated ZIP…")
            zip_path = build_batch_annotated_zip(batch, images, max_images=BATCH_ANNOTATED_ZIP_LIMIT)
            progress(1.0, desc="Batch complete")
            yield (
                format_field_batch_summary(batch),
                build_field_batch_dataframe(batch),
                status,
                batch_species_status_html(batch),
                _enabled_download(csv_path),
                _enabled_download(json_path),
                _enabled_download(zip_path),
                _enabled_download(wi_path),
                _enabled_download(inat_path),
                _enabled_download(eco_path),
                review_state,
                orig,
                ann,
                label,
                det_df,
                _review_panel_update(visible=True),
                batch,
            )
        else:
            progress(1.0, desc="Batch complete")

    except gr.Error:
        raise
    except Exception as exc:
        raise gr.Error(f"Batch failed: {exc}\n\n```\n{traceback.format_exc()}\n```") from exc


def _first_review_frame(review_state: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not review_state:
        return None
    for item in review_state:
        result = cast(AnalysisResult, item["result"])
        if result.animal_count > 0 and not result.error:
            return item
    return review_state[0]


def _load_frame_images(frame: dict[str, Any]) -> tuple[Image.Image, Image.Image]:
    result = cast(AnalysisResult, frame["result"])
    source_path = frame.get("source_path")
    if source_path:
        image = Image.open(source_path).convert("RGB")
    else:
        image = cast(Image.Image, frame["original"])
    if result.error:
        return image, image
    annotated = draw_detections(image, result.detections)
    return image, annotated


def _frame_view(
    frame: dict[str, Any] | None,
) -> tuple[Image.Image | None, Image.Image | None, str, pd.DataFrame]:
    if frame is None:
        return None, None, "", pd.DataFrame(columns=FIELD_DETECTION_COLUMNS)
    result = cast(AnalysisResult, frame["result"])
    label = f"**{frame['filename']}** — {result.animal_count} animals, {result.total} detections"
    original, annotated = _load_frame_images(frame)
    return original, annotated, label, build_minimal_detections_dataframe(result)


def load_lila_cache() -> tuple[list[str], str]:
    paths: list[Path] = []
    if LILA_CACHE_DIR.is_dir():
        for pattern in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
            paths.extend(LILA_CACHE_DIR.glob(pattern))
    files = sorted(str(path) for path in paths)
    if not files:
        raise gr.Error("LILA cache empty. Run:\n  python -m scripts.demo_batch --prepare-only")
    return files, f"**{len(files)}** images loaded — Process Folder or Quick demo."


def select_batch_frame(
    review_state: list[dict[str, Any]] | None,
    evt: gr.SelectData,
) -> tuple[Any, ...]:
    empty = (None, None, "", pd.DataFrame(columns=FIELD_DETECTION_COLUMNS), None, "")
    if not review_state or evt.index is None:
        return empty
    row = evt.index[0]
    if row < 0 or row >= len(review_state):
        return empty
    return (*_frame_view(review_state[row]), row, "")


def ai_review_frame(
    review_state: list[dict[str, Any]] | None,
    selected_index: int | None,
    progress: Any = gr.Progress(),  # noqa: B008
) -> str:
    if not review_state:
        return "Run a batch and select a frame first."
    idx = selected_index
    if idx is None or idx < 0 or idx >= len(review_state):
        first = _first_review_frame(review_state)
        idx = review_state.index(first) if first in review_state else 0
    frame = review_state[idx]
    result = cast(AnalysisResult, frame["result"])
    progress(0.2, desc="Sending frame to your LLM…")
    try:
        original, _annotated = _load_frame_images(frame)
    except Exception:
        original = None
    note = review_frame(result, original)
    progress(1.0, desc="AI review complete")
    return note


def clear_batch_review() -> tuple[Any, ...]:
    empty_table = pd.DataFrame(columns=FIELD_TABLE_COLUMNS)
    empty_det = pd.DataFrame(columns=FIELD_DETECTION_COLUMNS)
    return (
        EMPTY_FIELD_SUMMARY,
        empty_table,
        "Load LILA cache → Process Folder",
        probe_speciesnet(active=True),
        _disabled_download(),
        _disabled_download(),
        _disabled_download(),
        _disabled_download(),
        _disabled_download(),
        _disabled_download(),
        [],
        None,
        None,
        "",
        empty_det,
        _review_panel_update(visible=True),
        [],
        None,
    )


def run_quick_demo(
    files: list[str] | None,
    cache_paths: list[str] | None,
    threshold: float,
    progress: Any = gr.Progress(),  # noqa: B008
) -> Iterator[tuple[Any, ...]]:
    all_paths = _resolve_batch_paths(files, cache_paths)
    if not all_paths:
        yield _empty_batch_response("Load LILA cache first, then click **Quick demo**.")
        return

    cache_dir = all_paths[0].parent
    demo_paths = ensure_quick_demo_paths(cache_dir, threshold=threshold)
    if len(demo_paths) < QUICK_DEMO_COUNT:
        raise gr.Error(f"Quick demo needs {QUICK_DEMO_COUNT} frames — only {len(demo_paths)} matched.")

    yield from analyze_batch(
        files,
        cache_paths,
        threshold,
        classify_species=True,
        progress=progress,
        demo_paths=demo_paths,
        demo_mode=True,
    )


def refresh_species_status(enabled: bool) -> str:
    if enabled:
        threading.Thread(target=lambda: warmup_models(species=True), daemon=True).start()
    return probe_speciesnet(active=enabled)


def analyze_spot_check(
    image: Image.Image | None,
    threshold: float,
    classify_species: bool,
    progress: Any = gr.Progress(),  # noqa: B008
) -> tuple[Any, ...]:
    results = analyze_image(image, threshold=threshold, classify_species=classify_species, progress=progress)
    return results[0], results[1], results[3], results[4], results[5]


def analyze_video_ui(
    video_file: str | None,
    threshold: float,
    classify_species: bool,
    fps: float,
    max_frames: int,
    progress: Any = gr.Progress(),  # noqa: B008
) -> tuple[Any, ...]:
    if not video_file:
        raise gr.Error("Upload a video clip (MP4, AVI, MOV, MKV).")
    _reset_cancel()
    path = Path(video_file)

    def on_progress(current: int, total: int, message: str, fraction: float | None = None) -> None:
        frac = fraction if fraction is not None else current / max(total, 1)
        progress(frac, desc=message)

    try:
        result = analyze_video(
            path,
            fps=fps if fps > 0 else None,
            max_frames=int(max_frames),
            threshold=threshold,
            classify_species=classify_species,
            cancel_event=get_cancel_event(),
            progress_callback=on_progress,
        )
        out_dir = Path.home() / ".cache" / "biodex" / "video_exports"
        timeline = export_video_timeline(result, out_dir)
        summary = (
            f"**{result.total_frames}** frames · "
            f"**{len(result.key_frames)}** key frames · "
            f"**{sum(result.species_counts.values())}** species hits"
        )
        if result.interrupted:
            summary += " · **cancelled**"
        sampled = extract_frames(path, fps=fps if fps > 0 else None, max_frames=int(max_frames))
        by_index = {index: image for index, (_, image) in enumerate(sampled)}
        gallery = [
            draw_detections(by_index[idx], frame_result.detections)
            for idx, frame_result in result.key_frames
            if idx in by_index
        ]
        return (
            summary,
            _enabled_download(str(timeline)),
            gallery,
            _review_panel_update(visible=True),
        )
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def apply_settings(threshold: float, geofence: str) -> tuple[Any, ...]:
    save_settings(threshold=threshold, geofence_region=geofence)
    return (
        gr.update(value=threshold),
        "**Settings saved.**",
    )


def on_llm_provider_change(provider: str) -> tuple[Any, Any, Any]:
    provider = provider or DEFAULT_PROVIDER
    model = default_model(provider)
    return (
        gr.update(choices=flatten_models(provider), value=model),
        gr.update(visible=provider == "local"),
        gr.update(value=""),
    )


def save_llm_settings(provider: str, api_key: str, model: str, base_url: str) -> str:
    provider = provider or DEFAULT_PROVIDER
    model = model.strip()
    if key_required(provider) and not api_key.strip():
        return "Enter an API key."
    if not model:
        return "Enter a model name."
    save_settings(
        api_key=api_key.strip(),
        llm_provider=provider,
        llm_model=model,
        llm_base_url=base_url.strip() or DEFAULT_LOCAL_BASE_URL,
    )
    return "**Settings saved locally.**"


def clear_llm_settings() -> tuple[Any, ...]:
    save_settings(
        api_key="",
        llm_provider=DEFAULT_PROVIDER,
        llm_model=default_model(DEFAULT_PROVIDER),
        llm_base_url=DEFAULT_LOCAL_BASE_URL,
    )
    return (
        gr.update(value=DEFAULT_PROVIDER),
        gr.update(value=""),
        gr.update(choices=flatten_models(DEFAULT_PROVIDER), value=default_model(DEFAULT_PROVIDER)),
        gr.update(value=DEFAULT_LOCAL_BASE_URL, visible=False),
        "",
    )


def test_llm_settings(provider: str, api_key: str, model: str, base_url: str) -> str:
    result = test_connection(provider, api_key, model, base_url)
    if result == "Connected.":
        return f"**{result}**"
    return result


def toggle_api_menu(is_open: bool) -> tuple[bool, Any, Any, Any, Any, Any, Any]:
    new_open = not is_open
    if not new_open:
        return (
            new_open,
            gr.update(visible=False),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(value=""),
        )
    stored = load_settings()
    provider = stored.get("llm_provider", DEFAULT_PROVIDER)
    return (
        new_open,
        gr.update(visible=True),
        gr.update(value=provider),
        gr.update(value=stored.get("api_key", "")),
        gr.update(
            choices=flatten_models(provider),
            value=stored.get("llm_model") or default_model(provider),
        ),
        gr.update(
            value=stored.get("llm_base_url", DEFAULT_LOCAL_BASE_URL),
            visible=provider == "local",
        ),
        gr.update(value=""),
    )


def dashboard_stats(last_batch: BatchResult | None) -> str:
    if last_batch is None:
        return "<p>Run a batch to see quick stats here.</p>"
    return (
        f"<p><strong>{last_batch.total_images}</strong> images · "
        f"<strong>{last_batch.animal_count}</strong> animals · "
        f"<strong>{last_batch.blank_count}</strong> blanks</p>"
    )


__all__ = [
    "HOW_IT_WORKS",
    "ai_review_frame",
    "analyze_batch",
    "analyze_image",
    "analyze_spot_check",
    "analyze_video_ui",
    "apply_settings",
    "clear_llm_settings",
    "on_llm_provider_change",
    "save_llm_settings",
    "test_llm_settings",
    "toggle_api_menu",
    "clear_batch_review",
    "dashboard_stats",
    "load_lila_cache",
    "refresh_species_status",
    "request_cancel",
    "run_demo_mode",
    "run_quick_demo",
    "select_batch_frame",
    "try_demo",
]
