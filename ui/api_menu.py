"""Footer API settings menu (BYOK) — same flow as suggestio SettingsPanel."""

from __future__ import annotations

from typing import Any

import gradio as gr

from ui.llm_settings import (
    DEFAULT_LOCAL_BASE_URL,
    DEFAULT_PROVIDER,
    default_model,
    flatten_models,
    provider_choices,
)
from ui.settings_store import load_settings


def build_api_menu() -> dict[str, Any]:
    stored = load_settings()
    provider = stored.get("llm_provider", DEFAULT_PROVIDER)
    widgets: dict[str, Any] = {}
    with gr.Column(visible=False, elem_classes=["field-api-menu"]) as api_menu:
        gr.HTML(
            '<div class="field-api-menu-head">'
            '<span class="field-api-menu-title">LLM Settings</span>'
            '<span class="field-api-menu-sub">BYOK · stored locally · custom model IDs OK</span>'
            "</div>"
        )
        with gr.Row(elem_classes=["field-api-menu-grid"]):
            widgets["llm_provider"] = gr.Dropdown(
                choices=provider_choices(),
                value=provider,
                label="Provider",
                scale=1,
                container=False,
                elem_classes=["field-api-field"],
            )
            widgets["llm_model"] = gr.Dropdown(
                choices=flatten_models(provider),
                value=stored.get("llm_model") or default_model(provider),
                label="Model",
                allow_custom_value=True,
                scale=1,
                container=False,
                elem_classes=["field-api-field"],
            )
        widgets["llm_api_key"] = gr.Textbox(
            label="API key",
            placeholder="sk-…",
            type="password",
            value=stored.get("api_key", ""),
            container=False,
            elem_classes=["field-api-field"],
        )
        widgets["llm_base_url"] = gr.Textbox(
            label="Base URL",
            placeholder=DEFAULT_LOCAL_BASE_URL,
            value=stored.get("llm_base_url", DEFAULT_LOCAL_BASE_URL),
            visible=provider == "local",
            container=False,
            elem_classes=["field-api-field"],
        )
        with gr.Row(elem_classes=["field-api-menu-actions"], equal_height=True):
            widgets["llm_test_btn"] = gr.Button("Test", variant="secondary", scale=1, min_width=0)
            widgets["llm_save_btn"] = gr.Button("Save", variant="primary", scale=1, min_width=0)
            widgets["llm_clear_btn"] = gr.Button("Clear", scale=1, min_width=0)
        widgets["llm_status"] = gr.Markdown("", elem_classes=["field-api-status"])
    widgets["api_menu"] = api_menu
    return widgets


__all__ = ["build_api_menu"]
