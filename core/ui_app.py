"""
BioDex Gradio web application (v1.0).

Packaged entry point for ``biodex-ui`` — lives under ``core`` so pip installs
never shadow it with a stale top-level ``app.py`` in site-packages.
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any, cast

import gradio as gr
from ui.api_menu import build_api_menu
from ui.components import footer_chips_html, footer_tagline_html, header_html
from ui.handlers import (
    ai_review_frame,
    analyze_batch,
    analyze_spot_check,
    analyze_video_ui,
    apply_settings,
    clear_batch_review,
    clear_llm_settings,
    compute_analytics,
    load_lila_cache,
    on_llm_provider_change,
    refresh_species_status,
    request_cancel,
    run_quick_demo,
    save_llm_settings,
    select_batch_frame,
    test_llm_settings,
    toggle_api_menu,
)
from ui.styles import APP_THEME, CUSTOM_CSS, tree_background_css
from ui.tabs import (
    build_analytics_tab,
    build_batch_tab,
    build_dashboard_tab,
    build_settings_tab,
    build_video_tab,
)

from core.config import get_settings
from core.detector import warmup_models
from core.types import BIODEX_VERSION

_UI_DIR = Path(__file__).resolve().parent.parent / "ui"
LILA_CACHE_DIR = Path.home() / ".cache" / "biodex" / "channel-islands-demo"
FAVICON_PATH = _UI_DIR / "favicon.png"
TREE_BACKGROUND_PATH = _UI_DIR / "tree_of_life_background.jpg"
logger = logging.getLogger(__name__)


def build_app() -> gr.Blocks:
    """Construct the tabbed BioDex Gradio application."""
    settings = get_settings()
    page_classes = ["biodex-page"]

    with gr.Blocks(title=f"BioDex v{BIODEX_VERSION}") as demo:
        review_state = gr.State([])
        batch_paths_state = gr.State([])
        last_batch = gr.State(None)

        with gr.Column(elem_classes=[*page_classes, "field-device"]):
            gr.HTML(header_html())

            with gr.Tabs(elem_classes=["biodex-tabs"]):
                build_dashboard_tab(last_batch)
                batch_w = build_batch_tab(settings, review_state, batch_paths_state, last_batch)
                video_w = build_video_tab()
                analytics_w = build_analytics_tab(last_batch)
                settings_w = build_settings_tab()

            with gr.Column(elem_classes=["field-footer-section"]):
                gr.HTML(footer_tagline_html())
                api_open = gr.State(False)
                api_w = build_api_menu()
                with gr.Row(elem_classes=["field-footer-actions"]):
                    api_toggle_btn = gr.Button("Use via API", elem_classes=["field-api-toggle"])
                    gr.HTML(footer_chips_html())

        api_toggle_btn.click(
            fn=toggle_api_menu,
            inputs=[api_open],
            outputs=[
                api_open,
                api_w["api_menu"],
                api_w["llm_provider"],
                api_w["llm_api_key"],
                api_w["llm_model"],
                api_w["llm_base_url"],
                api_w["llm_status"],
            ],
        )
        api_w["llm_provider"].change(
            fn=on_llm_provider_change,
            inputs=[api_w["llm_provider"]],
            outputs=[api_w["llm_model"], api_w["llm_base_url"], api_w["llm_status"]],
        )
        api_w["llm_save_btn"].click(
            fn=save_llm_settings,
            inputs=[
                api_w["llm_provider"],
                api_w["llm_api_key"],
                api_w["llm_model"],
                api_w["llm_base_url"],
            ],
            outputs=[api_w["llm_status"]],
        )
        api_w["llm_test_btn"].click(
            fn=test_llm_settings,
            inputs=[
                api_w["llm_provider"],
                api_w["llm_api_key"],
                api_w["llm_model"],
                api_w["llm_base_url"],
            ],
            outputs=[api_w["llm_status"]],
        )
        api_w["llm_clear_btn"].click(
            fn=clear_llm_settings,
            outputs=[
                api_w["llm_provider"],
                api_w["llm_api_key"],
                api_w["llm_model"],
                api_w["llm_base_url"],
                api_w["llm_status"],
            ],
        )

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
                batch_w["review_panel"],
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
                batch_w["review_panel"],
                last_batch,
            ],
            show_progress="minimal",
        )
        for _reset_btn in (batch_w["batch_btn"], batch_w["quick_demo_btn"], batch_w["clear_btn"]):
            _reset_btn.click(
                fn=lambda: (None, ""),
                outputs=[batch_w["selected_frame_index"], batch_w["ai_review_output"]],
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
                batch_w["selected_frame_index"],
                batch_w["ai_review_output"],
            ],
        )
        batch_w["ai_review_btn"].click(
            fn=ai_review_frame,
            inputs=[batch_w["review_state"], batch_w["selected_frame_index"]],
            outputs=[batch_w["ai_review_output"]],
            show_progress="minimal",
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
                batch_w["review_panel"],
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
                video_w["video_results_panel"],
            ],
            show_progress="minimal",
        )
        video_w["video_cancel_btn"].click(fn=request_cancel, outputs=[video_w["video_status"]])

        analytics_w["analytics_refresh"].click(
            fn=compute_analytics,
            inputs=[last_batch],
            outputs=[
                analytics_w["diversity_html"],
                analytics_w["heatmap_image"],
                analytics_w["species_chart"],
                analytics_w["analytics_results_panel"],
            ],
        )

        settings_w["settings_save"].click(
            fn=apply_settings,
            inputs=[
                settings_w["settings_threshold"],
                settings_w["settings_geofence"],
            ],
            outputs=[
                batch_w["threshold"],
                settings_w["settings_status"],
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


def _find_open_port(host: str, preferred: int, attempts: int = 20) -> int:
    """Return the first open port at/after ``preferred`` (so a leftover BioDex doesn't block startup)."""
    import socket

    probe_host = "127.0.0.1" if host in ("0.0.0.0", "") else host
    for candidate in range(preferred, preferred + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if sock.connect_ex((probe_host, candidate)) != 0:
                return candidate
    return preferred


def launch_app() -> None:
    """Build and launch the Gradio UI (console entry: ``biodex-ui``)."""
    settings = get_settings()
    host = settings.host
    port = _find_open_port(host, settings.port)
    if port != settings.port:
        print(f"Port {settings.port} busy — using {port} instead.")
    css = CUSTOM_CSS + tree_background_css()
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
        "inbrowser": True,
        "allowed_paths": [str(biodex_cache), str(LILA_CACHE_DIR), str(TREE_BACKGROUND_PATH.parent)],
    }
    if FAVICON_PATH.is_file():
        launch_kwargs["favicon_path"] = str(FAVICON_PATH)
    app.launch(**launch_kwargs)


__all__ = ["build_app", "launch_app"]
