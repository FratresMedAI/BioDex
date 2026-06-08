"""
BioDex — Local AI for Wildlife Camera Traps (v0.5)

Gradio web UI with tabbed Dashboard, Batch, Video, Analytics, and Settings.
All inference runs locally.
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any, cast

import gradio as gr
from core.config import get_settings
from core.detector import warmup_models
from core.types import BIODEX_VERSION
from ui.components import footer_html, header_html
from ui.handlers import (
    analyze_batch,
    analyze_spot_check,
    analyze_video_ui,
    apply_settings,
    clear_batch_review,
    compute_analytics,
    load_lila_cache,
    refresh_species_status,
    request_cancel,
    run_quick_demo,
    select_batch_frame,
)
from ui.settings_store import load_settings
from ui.styles import APP_THEME, CUSTOM_CSS, dark_mode_css
from ui.tabs import (
    build_analytics_tab,
    build_batch_tab,
    build_dashboard_tab,
    build_settings_tab,
    build_video_tab,
)

LILA_CACHE_DIR = Path.home() / ".cache" / "biodex" / "channel-islands-demo"
FAVICON_PATH = Path(__file__).resolve().parent / "ui" / "favicon.png"
logger = logging.getLogger(__name__)


def build_app() -> gr.Blocks:
    """Construct the tabbed BioDex Gradio application."""
    settings = get_settings()
    stored = load_settings()
    page_class = "biodex-page biodex-dark" if stored.get("dark_mode") else "biodex-page"

    with gr.Blocks(title=f"BioDex v{BIODEX_VERSION}") as demo:
        review_state = gr.State([])
        batch_paths_state = gr.State([])
        last_batch = gr.State(None)

        with gr.Column(elem_classes=[page_class, "field-device"]) as page_column:
            gr.HTML(header_html())

            with gr.Tabs():
                build_dashboard_tab(last_batch)
                batch_w = build_batch_tab(settings, review_state, batch_paths_state, last_batch)
                video_w = build_video_tab()
                analytics_w = build_analytics_tab(last_batch)
                settings_w = build_settings_tab(page_column)

            gr.HTML(footer_html())

        # Batch tab wiring
        batch_w["classify_species"].change(
            fn=refresh_species_status,
            inputs=[batch_w["classify_species"]],
            outputs=[batch_w["species_status"]],
        )
        batch_w["load_cache_btn"].click(
            fn=load_lila_cache,
            outputs=[batch_w["batch_paths_state"], batch_w["batch_status"]],
        )
        batch_w["quick_demo_btn"].click(
            fn=run_quick_demo,
            inputs=[batch_w["batch_files"], batch_w["batch_paths_state"], batch_w["threshold"]],
            outputs=[
                batch_w["batch_stats"],
                batch_w["batch_table"],
                batch_w["batch_status"],
                batch_w["species_status"],
                batch_w["batch_csv_btn"],
                batch_w["batch_json_btn"],
                batch_w["batch_zip_btn"],
                batch_w["batch_wi_btn"],
                batch_w["batch_inat_btn"],
                batch_w["batch_eco_btn"],
                batch_w["review_state"],
                batch_w["review_original"],
                batch_w["review_annotated"],
                batch_w["frame_label"],
                batch_w["frame_detections"],
                last_batch,
            ],
            show_progress="minimal",
        )
        batch_w["batch_btn"].click(
            fn=analyze_batch,
            inputs=[
                batch_w["batch_files"],
                batch_w["batch_paths_state"],
                batch_w["threshold"],
                batch_w["classify_species"],
            ],
            outputs=[
                batch_w["batch_stats"],
                batch_w["batch_table"],
                batch_w["batch_status"],
                batch_w["species_status"],
                batch_w["batch_csv_btn"],
                batch_w["batch_json_btn"],
                batch_w["batch_zip_btn"],
                batch_w["batch_wi_btn"],
                batch_w["batch_inat_btn"],
                batch_w["batch_eco_btn"],
                batch_w["review_state"],
                batch_w["review_original"],
                batch_w["review_annotated"],
                batch_w["frame_label"],
                batch_w["frame_detections"],
                last_batch,
            ],
            show_progress="minimal",
        )
        batch_w["cancel_btn"].click(fn=request_cancel, outputs=[batch_w["batch_status"]])
        batch_w["batch_table"].select(
            fn=select_batch_frame,
            inputs=[batch_w["review_state"]],
            outputs=[
                batch_w["review_original"],
                batch_w["review_annotated"],
                batch_w["frame_label"],
                batch_w["frame_detections"],
            ],
        )
        batch_w["clear_btn"].click(
            fn=clear_batch_review,
            outputs=[
                batch_w["batch_stats"],
                batch_w["batch_table"],
                batch_w["batch_status"],
                batch_w["species_status"],
                batch_w["batch_csv_btn"],
                batch_w["batch_json_btn"],
                batch_w["batch_zip_btn"],
                batch_w["batch_wi_btn"],
                batch_w["batch_inat_btn"],
                batch_w["batch_eco_btn"],
                batch_w["review_state"],
                batch_w["review_original"],
                batch_w["review_annotated"],
                batch_w["frame_label"],
                batch_w["frame_detections"],
                batch_w["batch_paths_state"],
                last_batch,
            ],
        )
        batch_w["analyze_one_btn"].click(
            fn=analyze_spot_check,
            inputs=[batch_w["input_image"], batch_w["threshold"], batch_w["classify_species"]],
            outputs=[
                batch_w["spot_original"],
                batch_w["spot_annotated"],
                batch_w["spot_stats"],
                batch_w["spot_table"],
                batch_w["batch_status"],
            ],
            show_progress="minimal",
        )

        # Video tab
        video_w["video_analyze_btn"].click(
            fn=analyze_video_ui,
            inputs=[
                video_w["video_file"],
                video_w["video_threshold"],
                video_w["video_classify"],
                video_w["video_fps"],
                video_w["video_max_frames"],
            ],
            outputs=[
                video_w["video_status"],
                video_w["video_timeline_btn"],
                video_w["video_gallery"],
            ],
            show_progress="minimal",
        )
        video_w["video_cancel_btn"].click(fn=request_cancel, outputs=[video_w["video_status"]])

        # Analytics tab
        analytics_w["analytics_refresh"].click(
            fn=compute_analytics,
            inputs=[last_batch],
            outputs=[
                analytics_w["diversity_html"],
                analytics_w["heatmap_image"],
                analytics_w["species_chart"],
            ],
        )

        # Settings tab
        settings_w["settings_save"].click(
            fn=apply_settings,
            inputs=[
                settings_w["settings_threshold"],
                settings_w["settings_species"],
                settings_w["settings_dark"],
                settings_w["settings_geofence"],
            ],
            outputs=[
                batch_w["threshold"],
                batch_w["classify_species"],
                page_column,
            ],
        )

    return cast(gr.Blocks, demo)


def _start_model_warmup(*, species: bool = False) -> None:
    """Load MegaDetector in the background so Process Folder starts faster."""

    def _run() -> None:
        try:
            warmup_models(species=species)
            logger.info("Model warmup complete (species=%s).", species)
        except Exception as exc:
            logger.warning("Model warmup failed: %s", exc)

    threading.Thread(target=_run, daemon=True, name="biodex-warmup").start()


def launch_app() -> None:
    """Build and launch the Gradio UI (console entry: ``biodex-ui``)."""
    settings = get_settings()
    host = settings.host
    port = settings.port
    stored = load_settings()
    css = CUSTOM_CSS + (dark_mode_css() if stored.get("dark_mode") else "")
    print(f"BioDex v{BIODEX_VERSION} at http://{host}:{port}")
    print("Open the Batch tab to process a folder, or try Quick demo.")
    _start_model_warmup(species=True)
    app = build_app()
    if settings.enable_queue:
        app.queue(default_concurrency_limit=2)
    biodex_cache = Path.home() / ".cache" / "biodex"
    launch_kwargs: dict[str, Any] = {
        "server_name": host,
        "server_port": port,
        "theme": APP_THEME,
        "css": css,
        "auth": settings.gradio_auth,
        "show_error": True,
        "allowed_paths": [str(biodex_cache), str(LILA_CACHE_DIR)],
    }
    if FAVICON_PATH.is_file():
        launch_kwargs["favicon_path"] = str(FAVICON_PATH)
    app.launch(**launch_kwargs)


if __name__ == "__main__":
    launch_app()
