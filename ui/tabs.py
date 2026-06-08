"""Tab builders for the BioDex v1.0 Gradio UI."""

from __future__ import annotations

from typing import Any

import gradio as gr

from ui.components import (
    FIELD_DETECTION_COLUMNS,
    FIELD_TABLE_COLUMNS,
    RESULTS_COLUMNS,
    SPECIES_STATUS_INITIAL,
)
from ui.handlers import EMPTY_FIELD_SUMMARY, HOW_IT_WORKS, dashboard_stats
from ui.settings_store import load_settings


def build_dashboard_tab(last_batch: gr.State) -> tuple[gr.HTML, gr.Markdown]:
    with gr.Tab("Dashboard", id="dashboard"):
        gr.Markdown(HOW_IT_WORKS)
        stats = gr.HTML(dashboard_stats(None))
        last_batch.change(fn=dashboard_stats, inputs=[last_batch], outputs=[stats])
    return stats, gr.Markdown("")  # placeholder


def build_batch_tab(
    settings: Any,
    review_state: gr.State,
    batch_paths_state: gr.State,
    last_batch: gr.State,
) -> dict[str, Any]:
    """Build Batch tab components and return widget refs for wiring."""
    widgets: dict[str, Any] = {}

    with gr.Tab("Batch", id="batch"):
        widgets["batch_stats"] = gr.HTML(EMPTY_FIELD_SUMMARY, elem_classes=["field-stats-strip"])

        with gr.Row(elem_classes=["field-action-bar"]):
            widgets["load_cache_btn"] = gr.Button("Load LILA cache", scale=1, size="lg")
            widgets["quick_demo_btn"] = gr.Button("Quick demo", variant="secondary", scale=1, size="lg")
            widgets["batch_btn"] = gr.Button("Process Folder", variant="primary", scale=2, size="lg")
            widgets["cancel_btn"] = gr.Button("Cancel", variant="stop", scale=1)
            widgets["clear_btn"] = gr.Button("Clear", scale=1)

        widgets["batch_status"] = gr.Markdown(
            "Load LILA → Quick demo · Process Folder",
            elem_classes=["field-status-line"],
        )

        with gr.Row(elem_classes=["field-species-bar"]):
            widgets["classify_species"] = gr.Checkbox(
                value=load_settings().get("classify_species", True),
                label="Species classification (SpeciesNet)",
                scale=0,
            )
            widgets["species_status"] = gr.HTML(
                SPECIES_STATUS_INITIAL,
                elem_classes=["field-species-status"],
            )

        with gr.Accordion("Folder upload & threshold", open=False):
            widgets["batch_files"] = gr.File(
                label="Camera-trap folder",
                file_count="directory",
                file_types=["image"],
                type="filepath",
            )
            widgets["threshold"] = gr.Slider(
                minimum=0.05,
                maximum=0.95,
                value=load_settings().get("threshold", settings.default_threshold),
                step=0.05,
                label="Confidence threshold",
            )

        widgets["frame_label"] = gr.Markdown("", elem_classes=["field-frame-title"])
        with gr.Row(elem_classes=["field-image-panel", "field-viewer-row"]):
            widgets["review_original"] = gr.Image(
                label="Original", type="pil", interactive=False, height=420,
            )
            widgets["review_annotated"] = gr.Image(
                label="Annotated", type="pil", interactive=False, height=420,
            )

        widgets["batch_table"] = gr.Dataframe(
            headers=FIELD_TABLE_COLUMNS,
            label="Frames — click a row to review",
            interactive=False,
            wrap=True,
            elem_classes=["field-table-wrap"],
        )
        widgets["frame_detections"] = gr.Dataframe(
            headers=FIELD_DETECTION_COLUMNS,
            label="Detections in selected frame",
            interactive=False,
            wrap=True,
            elem_classes=["field-detections-wrap"],
        )

        with gr.Accordion("Export results", open=False):
            with gr.Row(elem_classes=["field-export-row"]):
                widgets["batch_csv_btn"] = gr.DownloadButton("Master CSV", interactive=False)
                widgets["batch_json_btn"] = gr.DownloadButton("Master JSON", interactive=False)
                widgets["batch_zip_btn"] = gr.DownloadButton("Annotated ZIP", variant="primary", interactive=False)
            with gr.Row(elem_classes=["field-export-row"]):
                widgets["batch_wi_btn"] = gr.DownloadButton("Wildlife Insights CSV", interactive=False)
                widgets["batch_inat_btn"] = gr.DownloadButton("iNaturalist draft", interactive=False)
                widgets["batch_eco_btn"] = gr.DownloadButton("EcoSentinel JSON", interactive=False)

        with gr.Accordion("Single-image spot check", open=False):
            widgets["input_image"] = gr.Image(label="Upload one image", type="pil", height=240)
            widgets["analyze_one_btn"] = gr.Button("Analyze", variant="secondary")
            with gr.Row():
                widgets["spot_original"] = gr.Image(label="Original", type="pil", interactive=False, height=280)
                widgets["spot_annotated"] = gr.Image(label="Annotated", type="pil", interactive=False, height=280)
            widgets["spot_stats"] = gr.HTML("")
            widgets["spot_table"] = gr.Dataframe(headers=RESULTS_COLUMNS, interactive=False, wrap=True)

    widgets["review_state"] = review_state
    widgets["batch_paths_state"] = batch_paths_state
    widgets["last_batch"] = last_batch
    return widgets


def build_video_tab() -> dict[str, Any]:
    widgets: dict[str, Any] = {}
    with gr.Tab("Video", id="video"):
        gr.Markdown("Upload a short camera-trap clip. Requires `pip install biodex[video]`.")
        widgets["video_file"] = gr.File(label="Video clip", file_types=[".mp4", ".avi", ".mov", ".mkv"], type="filepath")
        with gr.Row():
            widgets["video_fps"] = gr.Slider(0, 30, value=1, step=0.5, label="Sample FPS (0 = native)")
            widgets["video_max_frames"] = gr.Slider(10, 500, value=120, step=10, label="Max frames")
        widgets["video_classify"] = gr.Checkbox(value=False, label="Classify species")
        widgets["video_threshold"] = gr.Slider(0.05, 0.95, value=0.25, step=0.05, label="Threshold")
        widgets["video_analyze_btn"] = gr.Button("Analyze video", variant="primary")
        widgets["video_cancel_btn"] = gr.Button("Cancel", variant="stop")
        widgets["video_status"] = gr.Markdown("")
        widgets["video_timeline_btn"] = gr.DownloadButton("Timeline JSON", interactive=False)
        widgets["video_gallery"] = gr.Gallery(label="Key frames", columns=4, height=240)
    return widgets


def build_analytics_tab(last_batch: gr.State) -> dict[str, Any]:
    widgets: dict[str, Any] = {}
    with gr.Tab("Analytics", id="analytics"):
        gr.Markdown("Species diversity and activity patterns from your last batch run.")
        widgets["analytics_refresh"] = gr.Button("Refresh from last batch")
        widgets["diversity_html"] = gr.HTML("Run a batch first.")
        widgets["heatmap_image"] = gr.Image(label="Activity heatmap", interactive=False, height=280)
        widgets["species_chart"] = gr.HTML("")
        widgets["last_batch"] = last_batch
    return widgets


def build_settings_tab(page_column: gr.Column) -> dict[str, Any]:
    widgets: dict[str, Any] = {}
    stored = load_settings()
    with gr.Tab("Settings", id="settings"):
        gr.Markdown("Model and display preferences (saved locally).")
        widgets["settings_threshold"] = gr.Slider(0.05, 0.95, value=stored["threshold"], label="Default threshold")
        widgets["settings_species"] = gr.Checkbox(value=stored["classify_species"], label="Species classification default")
        widgets["settings_dark"] = gr.Checkbox(value=stored["dark_mode"], label="Dark mode")
        widgets["settings_geofence"] = gr.Dropdown(
            choices=["", "US", "AU", "EU", "SA", "AF"],
            value=stored.get("geofence_region", ""),
            label="Geofence region (experimental)",
        )
        widgets["settings_detector"] = gr.Dropdown(
            choices=["MDV5A"],
            value="MDV5A",
            label="Detector model",
            info="Additional models coming soon",
        )
        widgets["settings_save"] = gr.Button("Save settings", variant="primary")
        widgets["page_column"] = page_column
    return widgets


def build_shell(demo: gr.Blocks) -> gr.State:
    """Shared state for last batch result."""
    return gr.State(None)


__all__ = [
    "build_analytics_tab",
    "build_batch_tab",
    "build_dashboard_tab",
    "build_settings_tab",
    "build_shell",
    "build_video_tab",
]
