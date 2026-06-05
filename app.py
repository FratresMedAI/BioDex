"""
BioDex — Local AI for Wildlife Camera Traps (v0.4)

Gradio web UI for MegaDetector v5a detection, optional SpeciesNet classification,
and batch folder analysis. All inference runs locally.
"""

from __future__ import annotations

import traceback
from pathlib import Path
from typing import Any, cast

import gradio as gr
import pandas as pd
from core.batch import run_batch
from core.config import get_settings
from core.detector import analyze_single_image
from core.exports import (
    batch_to_csv,
    build_batch_annotated_zip,
    detections_to_csv,
    export_batch_json,
    export_bundle,
    export_json,
    save_annotated_image,
)
from core.types import BIODEX_VERSION, AnalysisResult
from core.visualization import draw_detections
from PIL import Image
from ui.components import (
    FIELD_DETECTION_COLUMNS,
    FIELD_TABLE_COLUMNS,
    RESULTS_COLUMNS,
    build_field_batch_dataframe,
    build_minimal_detections_dataframe,
    build_results_dataframe,
    footer_html,
    format_field_batch_summary,
    format_stats_html,
    header_html,
    load_sample_image,
)
from ui.styles import APP_THEME, CUSTOM_CSS

BATCH_ANNOTATED_ZIP_LIMIT = 100
LILA_CACHE_DIR = Path.home() / ".cache" / "biodex" / "channel-islands-demo"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
EMPTY_FIELD_SUMMARY = '<div class="field-summary field-summary-empty">No batch processed yet.</div>'

HOW_IT_WORKS = """
### How BioDex works

BioDex runs entirely on your computer. Your images are never uploaded to a cloud API.

**Step 1 — Detection (MegaDetector v5a)**  
[MegaDetector](https://github.com/agentmorris/MegaDetector) finds animals, people, and vehicles in camera trap images and returns bounding boxes with confidence scores.

**Step 2 — Species classification (optional)**  
When enabled, BioDex crops each animal detection and runs [SpeciesNet](https://github.com/google/cameratrapai) locally to suggest likely species. Borderline or uncertain predictions show alternatives for expert review.

**Step 3 — Batch mode**  
Upload multiple images at once to triage a folder. BioDex builds a summary table and exports a master CSV/JSON plus optional annotated image ZIP.

**Blank images:** An image is treated as a **blank** when no animal, person, or vehicle passes your confidence threshold.

**First run:** Model weights download once (MegaDetector ~280 MB; SpeciesNet ~214 MB if enabled), then analysis works offline.

**Species caveat:** SpeciesNet accuracy varies by region. Treat species labels as suggestions for expert review, not ground truth.
"""

SPECIES_TOGGLE_INFO = (
    "Identify species locally with SpeciesNet on animal crops. "
    "Typical runtime: ~5–15s on CPU. Downloads ~214 MB on first use."
)


def _disabled_download() -> Any:
    return gr.update(value=None, interactive=False)


def _enabled_download(path: str | None) -> Any:
    if path:
        return gr.update(value=path, interactive=True)
    return gr.update(value=None, interactive=False)


def load_sample_only() -> tuple[Image.Image, str, str]:
    """Load the bundled sample image into the upload control."""
    try:
        image, note = load_sample_image()
        return image, f'<div class="biodex-sample-note">{note}</div>', "**Status:** Sample loaded."
    except FileNotFoundError as exc:
        raise gr.Error(str(exc)) from exc


def run_demo_mode(progress: Any = gr.Progress()) -> tuple[Any, ...]:  # noqa: B008
    """Demo Mode: load sample, run detection + species, return full results."""
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
    # analyze_image returns 10 outputs; prepend enabled species toggle update
    return (gr.update(value=True),) + results


def try_demo(progress: Any = gr.Progress()) -> tuple[Any, ...]:  # noqa: B008
    """Backward-compatible alias used by tests or scripts."""
    return run_demo_mode(progress=progress)[1:]


def _format_model_error(exc: Exception) -> str:
    """Turn model-load/inference failures into actionable Gradio messages."""
    message = str(exc)
    lower = message.lower()
    if "megadetector" in lower or "failed to load" in lower:
        return (
            f"**MegaDetector error:** {message}\n\n"
            "First run downloads ~280 MB of weights. Check disk space, internet, "
            "and that `megadetector>=10.0,<11.0` is installed (not the unrelated 5.x package)."
        )
    if "speciesnet" in lower or "species" in lower:
        return (
            f"**SpeciesNet error:** {message}\n\n"
            "Species classification adds ~214 MB on first use. Try disabling species "
            "classification or use a fresh virtual environment if protobuf conflicts appear."
        )
    if "no space left" in lower or "disk full" in lower or isinstance(exc, OSError):
        return (
            f"**Storage error:** {message}\n\n"
            "Free disk space for model weights and temporary export files."
        )
    return (
        f"**Analysis failed:** {message}\n\n"
        "If this is your first run, model weights may still be downloading."
    )


def analyze_image(
    image: Image.Image | None,
    threshold: float,
    classify_species: bool,
    sample_note: str = "",
    progress: Any = gr.Progress(),  # noqa: B008
) -> tuple[Any, ...]:
    """Main single-image analysis handler."""
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
            if "Loading MegaDetector" in message:
                progress(0.15, desc=message)
            elif "SpeciesNet" in message:
                progress(0.55, desc=message)
            else:
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
    except ValueError as exc:
        raise gr.Error(str(exc)) from exc
    except RuntimeError as exc:
        raise gr.Error(_format_model_error(exc)) from exc
    except OSError as exc:
        raise gr.Error(_format_model_error(exc)) from exc
    except Exception as exc:
        tb = traceback.format_exc()
        raise gr.Error(
            f"{_format_model_error(exc)}\n\n```\n{tb}\n```"
        ) from exc


def analyze_batch(
    files: list[str] | None,
    threshold: float,
    classify_species: bool,
    progress: Any = gr.Progress(),  # noqa: B008
) -> tuple[Any, ...]:
    """Process an uploaded folder and prepare field-review outputs."""
    if not files:
        raise gr.Error("Select a camera-trap folder or load the LILA cache.")

    try:
        paths = sorted(
            Path(file_path)
            for file_path in files
            if Path(file_path).suffix.lower() in IMAGE_SUFFIXES
        )
        if not paths:
            raise gr.Error("No JPG/PNG images found in the upload.")

        images: list[tuple[str, Image.Image]] = []
        for path in paths:
            images.append((path.name, Image.open(path).convert("RGB")))

        def on_batch_progress(current: int, total: int, message: str) -> None:
            progress(current / total, desc=message)

        batch = run_batch(
            images,
            threshold=threshold,
            classify_species=classify_species,
            progress_callback=on_batch_progress,
        )

        review_state: list[dict[str, Any]] = []
        for result, (name, image) in zip(batch.results, images, strict=True):
            annotated = (
                draw_detections(image, result.detections)
                if not result.error
                else image
            )
            review_state.append(
                {
                    "filename": name,
                    "original": image,
                    "annotated": annotated,
                    "result": result,
                }
            )

        first = _first_review_frame(review_state)
        orig, ann, label, det_df = _frame_view(first)

        csv_path = batch_to_csv(batch)
        json_path = export_batch_json(batch)
        zip_path = build_batch_annotated_zip(
            batch,
            images,
            max_images=BATCH_ANNOTATED_ZIP_LIMIT,
        )

        progress(1.0, desc="Batch complete")
        status = (
            f"**{batch.total_images}** images · **{batch.animal_count}** animals · "
            f"**{sum(1 for r in batch.results if r.animal_count >= 2)}** multi-animal frames"
        )
        if batch.failed:
            status += f" · **{len(batch.failed)}** failed"

        return (
            format_field_batch_summary(batch),
            build_field_batch_dataframe(batch),
            status,
            _enabled_download(csv_path),
            _enabled_download(json_path),
            _enabled_download(zip_path),
            review_state,
            orig,
            ann,
            label,
            det_df,
        )

    except gr.Error:
        raise
    except Exception as exc:
        tb = traceback.format_exc()
        raise gr.Error(f"Batch failed: {exc}\n\n```\n{tb}\n```") from exc


def _first_review_frame(
    review_state: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if not review_state:
        return None
    for item in review_state:
        result = cast(AnalysisResult, item["result"])
        if result.animal_count > 0 and not result.error:
            return item
    return review_state[0]


def _frame_view(
    frame: dict[str, Any] | None,
) -> tuple[Image.Image | None, Image.Image | None, str, pd.DataFrame]:
    if frame is None:
        return None, None, "", pd.DataFrame(columns=FIELD_DETECTION_COLUMNS)
    result = cast(AnalysisResult, frame["result"])
    label = (
        f"**{frame['filename']}** — {result.animal_count} animals, "
        f"{result.total} detections"
    )
    return (
        cast(Image.Image, frame["original"]),
        cast(Image.Image, frame["annotated"]),
        label,
        build_minimal_detections_dataframe(result),
    )


def load_lila_cache() -> tuple[list[str], str]:
    """Load file paths from the local LILA demo cache."""
    paths: list[Path] = []
    if LILA_CACHE_DIR.is_dir():
        for pattern in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
            paths.extend(LILA_CACHE_DIR.glob(pattern))
    files = sorted(str(path) for path in paths)
    if not files:
        raise gr.Error(
            "LILA cache empty. Run:\n  python -m scripts.demo_batch --prepare-only"
        )
    return files, f"Loaded **{len(files)}** images from LILA cache."


def select_batch_frame(
    review_state: list[dict[str, Any]] | None,
    evt: gr.SelectData,
) -> tuple[Any, ...]:
    """Show original + annotated view for a selected table row."""
    if not review_state or evt.index is None:
        return None, None, "", pd.DataFrame(columns=FIELD_DETECTION_COLUMNS)
    row = evt.index[0]
    if row < 0 or row >= len(review_state):
        return None, None, "", pd.DataFrame(columns=FIELD_DETECTION_COLUMNS)
    orig, ann, label, det_df = _frame_view(review_state[row])
    return orig, ann, label, det_df


def clear_batch_review() -> tuple[Any, ...]:
    """Reset the field review panel."""
    empty_table = pd.DataFrame(columns=FIELD_TABLE_COLUMNS)
    empty_det = pd.DataFrame(columns=FIELD_DETECTION_COLUMNS)
    return (
        EMPTY_FIELD_SUMMARY,
        empty_table,
        "Ready.",
        _disabled_download(),
        _disabled_download(),
        _disabled_download(),
        [],
        None,
        None,
        "",
        empty_det,
    )


def analyze_spot_check(
    image: Image.Image | None,
    threshold: float,
    classify_species: bool,
    progress: Any = gr.Progress(),  # noqa: B008
) -> tuple[Any, ...]:
    """Single-image analysis for the collapsed spot-check panel."""
    results = analyze_image(
        image,
        threshold=threshold,
        classify_species=classify_species,
        progress=progress,
    )
    return results[0], results[1], results[3], results[4], results[5]


def build_app() -> gr.Blocks:
    """Construct the minimalist field-review Gradio application."""
    settings = get_settings()
    with gr.Blocks(title=f"BioDex Field Review v{BIODEX_VERSION}") as demo:
        review_state = gr.State([])

        with gr.Column(elem_classes=["biodex-page"]):
            gr.HTML(header_html())

            with gr.Row(elem_classes=["field-action-bar"]):
                batch_files = gr.File(
                    label="Camera-trap folder",
                    file_count="directory",
                    file_types=["image"],
                    type="filepath",
                    scale=3,
                )
                load_cache_btn = gr.Button("Load LILA cache", scale=1)
                batch_btn = gr.Button("Process Folder", variant="primary", scale=1)
                clear_btn = gr.Button("Clear", scale=1)

            batch_status = gr.Markdown("Select a folder or load the LILA cache.", elem_classes=["field-review-label"])

            with gr.Accordion("Settings", open=False):
                threshold = gr.Slider(
                    minimum=0.05,
                    maximum=0.95,
                    value=settings.default_threshold,
                    step=0.05,
                    label="Confidence threshold",
                )
                classify_species = gr.Checkbox(
                    value=True,
                    label="Species classification (SpeciesNet)",
                )

            batch_stats = gr.HTML(EMPTY_FIELD_SUMMARY)

            frame_label = gr.Markdown("", elem_classes=["field-review-label"])
            with gr.Row(elem_classes=["field-image-panel"]):
                review_original = gr.Image(
                    label="Original",
                    type="pil",
                    interactive=False,
                    height=480,
                    elem_classes=["field-image-panel"],
                )
                review_annotated = gr.Image(
                    label="Annotated",
                    type="pil",
                    interactive=False,
                    height=480,
                    elem_classes=["field-image-panel"],
                )

            with gr.Column(elem_classes=["field-table-wrap"]):
                batch_table = gr.Dataframe(
                    headers=FIELD_TABLE_COLUMNS,
                    label="Frames — click a row to review",
                    interactive=False,
                    wrap=True,
                )

            frame_detections = gr.Dataframe(
                headers=FIELD_DETECTION_COLUMNS,
                label="Detections in selected frame",
                interactive=False,
                wrap=True,
            )

            with gr.Row(elem_classes=["field-export-row"]):
                batch_csv_btn = gr.DownloadButton("Master CSV", interactive=False)
                batch_json_btn = gr.DownloadButton("Master JSON", interactive=False)
                batch_zip_btn = gr.DownloadButton("Annotated ZIP", variant="primary", interactive=False)

            with gr.Accordion("Single-image spot check", open=False):
                with gr.Row():
                    input_image = gr.Image(label="Upload one image", type="pil", height=240)
                    analyze_one_btn = gr.Button("Analyze", variant="secondary")
                with gr.Row():
                    spot_original = gr.Image(label="Original", type="pil", interactive=False, height=280)
                    spot_annotated = gr.Image(label="Annotated", type="pil", interactive=False, height=280)
                spot_stats = gr.HTML("")
                spot_table = gr.Dataframe(headers=RESULTS_COLUMNS, interactive=False, wrap=True)

            gr.HTML(footer_html())

            load_cache_btn.click(
                fn=load_lila_cache,
                outputs=[batch_files, batch_status],
            )

            batch_btn.click(
                fn=analyze_batch,
                inputs=[batch_files, threshold, classify_species],
                outputs=[
                    batch_stats,
                    batch_table,
                    batch_status,
                    batch_csv_btn,
                    batch_json_btn,
                    batch_zip_btn,
                    review_state,
                    review_original,
                    review_annotated,
                    frame_label,
                    frame_detections,
                ],
                show_progress="full",
            )

            batch_table.select(
                fn=select_batch_frame,
                inputs=[review_state],
                outputs=[review_original, review_annotated, frame_label, frame_detections],
            )

            clear_btn.click(
                fn=clear_batch_review,
                outputs=[
                    batch_stats,
                    batch_table,
                    batch_status,
                    batch_csv_btn,
                    batch_json_btn,
                    batch_zip_btn,
                    review_state,
                    review_original,
                    review_annotated,
                    frame_label,
                    frame_detections,
                ],
            )

            analyze_one_btn.click(
                fn=analyze_spot_check,
                inputs=[input_image, threshold, classify_species],
                outputs=[
                    spot_original,
                    spot_annotated,
                    spot_stats,
                    spot_table,
                    batch_status,
                ],
                show_progress="full",
            )

    return cast(gr.Blocks, demo)


def launch_app() -> None:
    """Build and launch the Gradio UI (console entry: ``biodex-ui``)."""
    settings = get_settings()
    host = settings.host
    port = settings.port
    print(f"BioDex Field Review v{BIODEX_VERSION} at http://{host}:{port}")
    print("Load a folder or click Load LILA cache, then Process Folder.")
    app = build_app()
    app.launch(
        server_name=host,
        server_port=port,
        theme=APP_THEME,
        css=CUSTOM_CSS,
    )


if __name__ == "__main__":
    launch_app()
