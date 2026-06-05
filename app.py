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
from core.types import BIODEX_VERSION
from core.visualization import draw_detections
from PIL import Image
from ui.components import (
    BATCH_COLUMNS,
    RESULTS_COLUMNS,
    build_batch_dataframe,
    build_results_dataframe,
    demo_tab_intro_html,
    footer_html,
    format_batch_stats_html,
    format_stats_html,
    header_html,
    load_sample_image,
    welcome_html,
)
from ui.styles import APP_THEME, CUSTOM_CSS

BATCH_ANNOTATED_ZIP_LIMIT = 50

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
    """Analyze multiple uploaded images."""
    if not files:
        raise gr.Error("Please upload one or more camera trap images.")

    try:
        images: list[tuple[str, Image.Image]] = []
        for file_path in files:
            upload_path = Path(file_path)
            images.append((upload_path.name, Image.open(upload_path).convert("RGB")))

        def on_batch_progress(current: int, total: int, message: str) -> None:
            progress(current / total, desc=message)

        batch = run_batch(
            images,
            threshold=threshold,
            classify_species=classify_species,
            progress_callback=on_batch_progress,
        )

        stats_html = format_batch_stats_html(batch)
        batch_df = build_batch_dataframe(batch)
        csv_path = batch_to_csv(batch)
        json_path = export_batch_json(batch)

        zip_path = build_batch_annotated_zip(
            batch,
            images,
            max_images=BATCH_ANNOTATED_ZIP_LIMIT,
        )

        progress(1.0, desc="Batch analysis complete")

        return (
            stats_html,
            batch_df,
            "**Status:** Batch analysis complete.",
            _enabled_download(csv_path),
            _enabled_download(json_path),
            _enabled_download(zip_path),
        )

    except gr.Error:
        raise
    except Exception as exc:
        tb = traceback.format_exc()
        raise gr.Error(
            f"Batch analysis failed: {exc}\n\n"
            f"Details:\n```\n{tb}\n```"
        ) from exc


def build_app() -> gr.Blocks:
    """Construct and return the Gradio Blocks application."""
    settings = get_settings()
    with gr.Blocks(title=f"BioDex v{BIODEX_VERSION}") as demo:
        with gr.Column(elem_classes=["biodex-page"]):
            gr.HTML(header_html())
            gr.HTML(welcome_html())

            with gr.Column(elem_classes=["biodex-section", "biodex-demo-section"]):
                gr.Markdown("Demo Mode", elem_classes=["biodex-demo-title"])
                gr.HTML(demo_tab_intro_html())
                run_demo_btn = gr.Button(
                    "Run Demo",
                    variant="primary",
                    size="lg",
                    elem_classes=["biodex-run-demo-btn"],
                )
                demo_status = gr.Markdown(
                    "**Status:** Ready — click **Run Demo** for a one-click walkthrough.",
                    elem_classes=["biodex-status-wrap"],
                )
                demo_sample_note = gr.HTML("")

                with gr.Row():
                    demo_original = gr.Image(
                        label="Original",
                        type="pil",
                        interactive=False,
                        height=360,
                    )
                    demo_annotated = gr.Image(
                        label="Annotated detections",
                        type="pil",
                        interactive=False,
                        height=360,
                    )

                demo_stats = gr.HTML(label="Demo summary")
                demo_results = gr.Dataframe(
                    headers=RESULTS_COLUMNS,
                    label="Detections",
                    interactive=False,
                    wrap=True,
                )

                gr.Markdown("Export demo results", elem_classes=["biodex-export-label"])
                with gr.Row(elem_classes=["biodex-export-row"]):
                    demo_dl_image = gr.DownloadButton(
                        "Annotated image (PNG)",
                        variant="secondary",
                        interactive=False,
                    )
                    demo_dl_csv = gr.DownloadButton(
                        "Detections (CSV)",
                        variant="secondary",
                        interactive=False,
                    )
                    demo_dl_json = gr.DownloadButton(
                        "Results (JSON)",
                        variant="secondary",
                        interactive=False,
                    )
                    demo_dl_bundle = gr.DownloadButton(
                        "Download All (ZIP)",
                        variant="primary",
                        interactive=False,
                    )

            with gr.Column(elem_classes=["biodex-section", "biodex-workspace"]):
                gr.Markdown("### Analyze images", elem_classes=["biodex-section-title"])
                gr.Markdown("Analysis settings", elem_classes=["biodex-settings-label"])
                with gr.Row():
                    threshold = gr.Slider(
                        minimum=0.05,
                        maximum=0.95,
                        value=settings.default_threshold,
                        step=0.05,
                        label="Confidence threshold",
                        info="Higher = fewer, more confident detections",
                        scale=2,
                    )
                classify_species = gr.Checkbox(
                    value=settings.default_classify_species,
                    label="Enable species classification (SpeciesNet)",
                    info=SPECIES_TOGGLE_INFO,
                )
                gr.Markdown(
                    "Runs locally on animal crops. Adds ~5–15s on CPU. "
                    "Borderline predictions show alternatives in the results table.",
                    elem_classes=["biodex-species-note"],
                )

                with gr.Tabs(elem_classes=["biodex-tabs"]):
                    with gr.Tab("Single Image", elem_classes=["biodex-tab"]):
                        with gr.Row():
                            with gr.Column(scale=1):
                                input_image = gr.Image(
                                    label="Upload camera trap image",
                                    type="pil",
                                    sources=["upload"],
                                    height=300,
                                )
                                sample_note = gr.HTML("")
                                with gr.Row():
                                    sample_btn = gr.Button(
                                        "Load sample image",
                                        size="sm",
                                        elem_classes=["biodex-secondary-btn"],
                                    )
                                analyze_btn = gr.Button(
                                    "Analyze Image",
                                    variant="primary",
                                    size="lg",
                                    elem_classes=["biodex-primary-action"],
                                )
                                status_md = gr.Markdown(
                                    "**Status:** Ready.",
                                    elem_classes=["biodex-status-wrap"],
                                )

                            with gr.Column(scale=1):
                                gr.Markdown(
                                    """
                                    **Tips**
                                    - New here? Try **Run Demo** in the section above.
                                    - Enable species classification to identify animals.
                                    - Export PNG, CSV, JSON, or a ZIP bundle after analysis.
                                    """,
                                    elem_classes=["biodex-tab-tips"],
                                )

                        with gr.Row():
                            original_out = gr.Image(
                                label="Original",
                                type="pil",
                                interactive=False,
                                height=400,
                            )
                            annotated_out = gr.Image(
                                label="Annotated detections",
                                type="pil",
                                interactive=False,
                                height=400,
                            )

                        stats_panel = gr.HTML(label="Analysis summary")
                        results_table = gr.Dataframe(
                            headers=RESULTS_COLUMNS,
                            label="Detections",
                            interactive=False,
                            wrap=True,
                        )

                        gr.Markdown("Export results", elem_classes=["biodex-export-label"])
                        with gr.Row(elem_classes=["biodex-export-row"]):
                            download_image = gr.DownloadButton(
                                "Annotated image (PNG)",
                                variant="secondary",
                                interactive=False,
                            )
                            download_csv = gr.DownloadButton(
                                "Detections (CSV)",
                                variant="secondary",
                                interactive=False,
                            )
                            download_json = gr.DownloadButton(
                                "Results (JSON)",
                                variant="secondary",
                                interactive=False,
                            )
                            download_bundle = gr.DownloadButton(
                                "Download All (ZIP)",
                                variant="primary",
                                interactive=False,
                            )

                        sample_btn.click(
                            fn=load_sample_only,
                            outputs=[input_image, sample_note, status_md],
                        )

                        analyze_btn.click(
                            fn=analyze_image,
                            inputs=[input_image, threshold, classify_species],
                            outputs=[
                                original_out,
                                annotated_out,
                                sample_note,
                                stats_panel,
                                results_table,
                                status_md,
                                download_image,
                                download_csv,
                                download_json,
                                download_bundle,
                            ],
                            show_progress="full",
                        )

                    with gr.Tab("Batch Folder", elem_classes=["biodex-tab"]):
                        with gr.Row():
                            with gr.Column(scale=1):
                                batch_files = gr.File(
                                    label="Upload multiple images",
                                    file_count="multiple",
                                    file_types=["image"],
                                    type="filepath",
                                )
                                batch_btn = gr.Button(
                                    "Analyze Batch",
                                    variant="primary",
                                    size="lg",
                                    elem_classes=["biodex-primary-action"],
                                )
                                batch_status = gr.Markdown(
                                    "**Status:** Ready.",
                                    elem_classes=["biodex-status-wrap"],
                                )
                            with gr.Column(scale=1):
                                gr.Markdown(
                                    """
                                    **Batch workflow**
                                    1. Select multiple JPG/PNG files from a folder
                                    2. Uses the shared threshold and species settings above
                                    3. Review the summary table and export master CSV/JSON
                                    4. Download annotated images ZIP (first 50 images)
                                    """,
                                    elem_classes=["biodex-tab-tips"],
                                )

                        batch_stats = gr.HTML(label="Batch summary")
                        batch_table = gr.Dataframe(
                            headers=BATCH_COLUMNS,
                            label="Per-image results",
                            interactive=False,
                            wrap=True,
                        )

                        gr.Markdown("Batch export", elem_classes=["biodex-export-label"])
                        with gr.Row(elem_classes=["biodex-export-row"]):
                            batch_csv_btn = gr.DownloadButton(
                                "Master CSV",
                                variant="secondary",
                                interactive=False,
                            )
                            batch_json_btn = gr.DownloadButton(
                                "Master JSON",
                                variant="secondary",
                                interactive=False,
                            )
                            batch_zip_btn = gr.DownloadButton(
                                "Annotated images ZIP",
                                variant="primary",
                                interactive=False,
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
                            ],
                            show_progress="full",
                        )

            run_demo_btn.click(
                fn=run_demo_mode,
                outputs=[
                    classify_species,
                    demo_original,
                    demo_annotated,
                    demo_sample_note,
                    demo_stats,
                    demo_results,
                    demo_status,
                    demo_dl_image,
                    demo_dl_csv,
                    demo_dl_json,
                    demo_dl_bundle,
                ],
                show_progress="full",
            )

            with gr.Accordion("How it works", open=False):
                gr.Markdown(HOW_IT_WORKS)

            gr.HTML(footer_html())

    return cast(gr.Blocks, demo)


def launch_app() -> None:
    """Build and launch the Gradio UI (console entry: ``biodex-ui``)."""
    settings = get_settings()
    host = settings.host
    port = settings.port
    print(f"BioDex v{BIODEX_VERSION} starting at http://{host}:{port}")
    print("Open the app — Demo Mode is at the top, analysis tabs are in the workspace below.")
    app = build_app()
    app.launch(
        server_name=host,
        server_port=port,
        theme=APP_THEME,
        css=CUSTOM_CSS,
    )


if __name__ == "__main__":
    launch_app()
