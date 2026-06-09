"""BioDex Gradio UI theme and custom styles."""

import base64
from pathlib import Path

import gradio as gr

# Warm, earthy dark palette — forest greens + amber/terracotta glass over the savanna.
_BD_CREAM = "#17150f"  # app base (warm near-black behind glass)
_BD_SURFACE = "#262019"  # raised warm surface
_BD_SAGE = "#2c2820"  # table odd / hover
_BD_SAND = "#231e17"  # input / card fill
_BD_BORDER = "#48402f"  # warm subtle border
_BD_MOSS = "#86c193"  # forest sage green (primary)
_BD_MOSS_HOVER = "#99d0a5"
_BD_EARTH = "#e0a95e"  # warm amber/gold accent
_BD_TEXT = "#f2ede2"  # warm off-white
_BD_TEXT_MUTED = "#b6a98f"  # warm taupe
_BD_ON_PRIMARY = "#12200f"  # text on green buttons

APP_THEME = (
    gr.themes.Soft(
        primary_hue=gr.themes.colors.green,
        secondary_hue=gr.themes.colors.emerald,
        neutral_hue=gr.themes.colors.stone,
    )
    .set(
        body_background_fill=_BD_CREAM,
        body_background_fill_dark=_BD_CREAM,
        background_fill_primary=_BD_CREAM,
        background_fill_primary_dark=_BD_CREAM,
        background_fill_secondary=_BD_CREAM,
        background_fill_secondary_dark=_BD_CREAM,
        block_background_fill=_BD_CREAM,
        block_background_fill_dark=_BD_CREAM,
        block_border_color=_BD_TEXT,
        block_border_color_dark=_BD_TEXT,
        block_label_text_color=_BD_TEXT,
        block_label_text_color_dark=_BD_TEXT,
        block_title_text_color=_BD_TEXT,
        block_title_text_color_dark=_BD_TEXT,
        body_text_color=_BD_TEXT,
        body_text_color_dark=_BD_TEXT,
        body_text_color_subdued=_BD_TEXT_MUTED,
        body_text_color_subdued_dark=_BD_TEXT_MUTED,
        border_color_primary=_BD_BORDER,
        border_color_primary_dark=_BD_BORDER,
        button_primary_background_fill=_BD_MOSS,
        button_primary_background_fill_dark=_BD_MOSS,
        button_primary_background_fill_hover=_BD_MOSS_HOVER,
        button_primary_background_fill_hover_dark=_BD_MOSS_HOVER,
        button_primary_text_color=_BD_ON_PRIMARY,
        button_primary_text_color_dark=_BD_ON_PRIMARY,
        button_secondary_background_fill=_BD_SURFACE,
        button_secondary_background_fill_dark=_BD_SURFACE,
        button_secondary_background_fill_hover=_BD_SAGE,
        button_secondary_background_fill_hover_dark=_BD_SAGE,
        button_secondary_text_color=_BD_TEXT,
        button_secondary_text_color_dark=_BD_TEXT,
        button_secondary_border_color=_BD_BORDER,
        button_secondary_border_color_dark=_BD_BORDER,
        input_background_fill=_BD_SAND,
        input_background_fill_dark=_BD_SAND,
        input_border_color=_BD_BORDER,
        input_border_color_dark=_BD_BORDER,
        slider_color=_BD_MOSS,
        slider_color_dark=_BD_MOSS,
        checkbox_background_color=_BD_SAND,
        checkbox_background_color_dark=_BD_SAND,
        checkbox_label_background_fill="transparent",
        checkbox_label_background_fill_dark="transparent",
        checkbox_label_background_fill_selected="transparent",
        checkbox_label_background_fill_selected_dark="transparent",
        checkbox_label_text_color=_BD_TEXT,
        checkbox_label_text_color_dark=_BD_TEXT,
        table_even_background_fill=_BD_SAND,
        table_even_background_fill_dark=_BD_SAND,
        table_odd_background_fill=_BD_SAGE,
        table_odd_background_fill_dark=_BD_SAGE,
    )
)

CUSTOM_CSS = """
:root {
    --bd-cream: #17150f;
    --bd-surface: rgba(54, 44, 31, 0.5);
    --bd-sage: rgba(60, 52, 36, 0.46);
    --bd-sage-deep: rgba(38, 32, 22, 0.9);
    --bd-sand: rgba(45, 37, 26, 0.58);
    --bd-tan: rgba(66, 56, 40, 0.5);
    --bd-border: rgba(224, 198, 138, 0.18);
    --bd-border-strong: rgba(224, 198, 138, 0.3);
    --bd-moss: #86c193;
    --bd-moss-hover: #99d0a5;
    --bd-earth: #e0a95e;
    --bd-text: #f2ede2;
    --bd-line: rgba(224, 198, 138, 0.18);
    --bd-text-muted: #b6a98f;
    --bd-amber: #e7b85c;
    --bd-terracotta: #e0916a;
    --bd-radius-sm: 12px;
    --bd-glass-shadow: 0 24px 70px rgba(8, 6, 2, 0.5);
}

/* Page shell */
.gradio-container,
.dark .gradio-container {
    color-scheme: dark !important;
    background: var(--bd-cream) !important;
    max-width: 960px !important;
    margin: 0 auto !important;
    font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif !important;
    font-size: 15.5px !important;
    line-height: 1.6 !important;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
    position: relative;
    isolation: isolate;
}
.gradio-container .main,
.gradio-container .wrap,
.gradio-container .contain,
.dark .gradio-container .main,
.dark .gradio-container .wrap {
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
    box-shadow: none !important;
}
.gradio-container:has(.biodex-page) {
    background: transparent !important;
}

/* Flatten layout chrome only — keep borders on widgets */
.biodex-page .group,
.biodex-page .column,
.biodex-page .row {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.biodex-page .block,
.biodex-page .form,
.biodex-page .block.padded {
    background: transparent !important;
    box-shadow: none !important;
}
.biodex-page .gap {
    gap: 0.85rem !important;
}

.biodex-shell {
    max-width: 100%;
    margin: 0 auto;
}

/* ── Page background (always on when image is present) ── */
.biodex-page::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: -2;
    pointer-events: none;
    background-size: cover;
    background-position: center center;
    background-attachment: fixed;
    background-repeat: no-repeat;
}

/* Fallback gradient if banner is missing/unavailable. */
.biodex-page::after {
    content: "";
    position: fixed;
    inset: 0;
    z-index: -3;
    pointer-events: none;
    background: radial-gradient(circle at 20% 15%, #3a3326 0%, #241d14 55%, #100d08 100%);
}

/* No outer box — the full savanna background shows through. */
.biodex-page {
    background: transparent;
    border: none;
    box-shadow: none;
    padding: 1rem 1.25rem 1.4rem;
    color: var(--bd-text);
}
/* Floating text (not inside a glass box) stays readable over the photo. */
.biodex-page,
.biodex-page .prose,
.biodex-page .prose p,
.biodex-page .markdown p,
.biodex-page h1,
.biodex-page h2,
.biodex-page h3,
.biodex-tabs button {
    text-shadow: 0 1px 6px rgba(0, 0, 0, 0.65), 0 1px 2px rgba(0, 0, 0, 0.5);
}

/* ── Header (single soft card) ── */
.biodex-header {
    text-align: center;
    margin-bottom: 0.25rem;
    padding: 1.5rem 1rem 1.15rem;
    background: linear-gradient(180deg, rgba(60, 52, 36, 0.32) 0%, transparent 90%);
    border-radius: var(--bd-radius-sm);
}
.biodex-header h1 {
    margin: 0 0 0.25rem 0;
    font-family: Georgia, "Times New Roman", serif;
    font-weight: 700;
    font-size: 2.05rem;
    letter-spacing: 0.01em;
    color: var(--bd-text);
}
.biodex-header .biodex-title-accent {
    color: var(--bd-moss);
}
.biodex-tagline {
    color: var(--bd-text-muted);
    font-size: 0.98rem;
    margin: 0.3rem 0 0.75rem;
    line-height: 1.5;
    max-width: 34rem;
    margin-left: auto;
    margin-right: auto;
}
.biodex-badge-row {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.biodex-badge {
    padding: 0.22rem 0.75rem;
    border-radius: 999px;
    font-size: 0.76rem;
    font-weight: 600;
}
.biodex-badge-version {
    color: var(--bd-moss);
    background: transparent;
    border: 1px solid var(--bd-border);
}
.biodex-badge-privacy {
    color: var(--bd-earth);
    background: transparent;
    border: 1px solid var(--bd-border);
}

/* ── Welcome — flat steps, no inner boxes ── */
.biodex-welcome {
    padding: 0.75rem 0 1rem;
    border-bottom: 1px solid var(--bd-line);
}
.biodex-welcome h3 {
    margin: 0 0 0.6rem 0;
    color: var(--bd-moss);
    font-size: 0.9rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.biodex-welcome-steps {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    list-style: none;
    margin: 0;
    padding: 0;
}
@media (max-width: 768px) {
    .biodex-welcome-steps { grid-template-columns: 1fr; }
}
.biodex-welcome-step {
    color: var(--bd-text-muted);
    font-size: 0.95rem;
    line-height: 1.55;
    padding: 0;
}
.biodex-welcome-step-num {
    color: var(--bd-moss);
    font-weight: 700;
    margin-right: 0.35rem;
}
.biodex-welcome strong {
    color: var(--bd-text);
}

/* ── Sections — divider only, no card wrapper ── */
.biodex-section {
    padding: 1.35rem 0 !important;
    border-bottom: 1px solid var(--bd-line);
}
.biodex-section-title,
.biodex-section-title p {
    font-weight: 700 !important;
    color: var(--bd-text) !important;
    font-size: 1.18rem !important;
    letter-spacing: 0.01em !important;
    margin: 0 0 1rem 0 !important;
}
.biodex-settings-label,
.biodex-settings-label p {
    font-weight: 600 !important;
    color: var(--bd-text-muted) !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin: 0 0 0.65rem 0 !important;
}

/* ── Demo — flat, no nested hero box ── */
.biodex-demo-title,
.biodex-demo-title p {
    font-family: Georgia, "Times New Roman", serif !important;
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    color: var(--bd-moss) !important;
    margin: 0 0 0.5rem 0 !important;
}
.biodex-demo-hero {
    margin-bottom: 0.85rem;
    color: var(--bd-text-muted);
}
.biodex-demo-hero p {
    margin: 0.25rem 0;
    line-height: 1.5;
    font-size: 0.92rem;
}
.biodex-demo-detail {
    font-size: 0.86rem;
}
.biodex-demo-hero strong {
    color: var(--bd-text);
}
.biodex-demo-callout {
    display: inline-block;
    margin-top: 0.4rem;
    font-size: 0.82rem;
    color: var(--bd-moss);
    font-weight: 600;
}
.biodex-run-demo-btn {
    margin: 0.25rem 0 0.65rem !important;
}
.biodex-run-demo-btn button {
    min-width: 200px;
}

/* ── Species toggle — inline, no card ── */
.biodex-species-note,
.biodex-species-note p {
    font-size: 0.84rem !important;
    color: var(--bd-text-muted) !important;
    margin: 0.15rem 0 0.75rem 0 !important;
    line-height: 1.4 !important;
}

/* ── Tabs — minimal underline style ── */
.biodex-tabs {
    margin-top: 0.75rem !important;
}
.biodex-tabs > .tab-nav,
.biodex-tabs .tab-nav {
    background: transparent !important;
    border: none !important;
    border-bottom: 1px solid var(--bd-line) !important;
    border-radius: 0 !important;
    padding: 0 !important;
    gap: 0 !important;
    margin-bottom: 1.1rem !important;
}
.biodex-tabs button,
.biodex-tabs .tab-nav button {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    color: var(--bd-text-muted) !important;
    font-weight: 600 !important;
    font-size: 0.98rem !important;
    letter-spacing: 0.01em !important;
    padding: 0.7rem 1.15rem !important;
    box-shadow: none !important;
    transition: color 0.18s ease, border-color 0.18s ease !important;
}
.biodex-tabs button:hover,
.biodex-tabs .tab-nav button:hover {
    color: var(--bd-text) !important;
}
.biodex-tabs button.selected,
.biodex-tabs .tab-nav button.selected {
    color: var(--bd-moss) !important;
    font-weight: 700 !important;
    border-bottom: 2px solid var(--bd-moss) !important;
    background: linear-gradient(180deg, rgba(134, 193, 147, 0.12) 0%, transparent 100%) !important;
}

/* Markdown / prose — readable on warm field palette */
.biodex-page .prose,
.biodex-page .prose p,
.biodex-page .markdown p {
    color: #e9e2d4 !important;
}
.biodex-page .prose code,
.biodex-page .markdown code,
.biodex-page .prose pre code,
.biodex-page .markdown pre code {
    background: var(--bd-sand) !important;
    color: var(--bd-moss) !important;
    border: 1px solid var(--bd-border) !important;
    padding: 0.1rem 0.42rem !important;
    border-radius: 5px !important;
    font-size: 0.9em !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}

/* Tips — plain text, no box */
.biodex-tab-tips,
.biodex-tab-tips p {
    color: var(--bd-text-muted) !important;
    font-size: 0.88rem !important;
    line-height: 1.55 !important;
    margin: 0 !important;
}

/* Status — plain inline text */
.biodex-status-wrap p {
    color: var(--bd-text-muted) !important;
    font-size: 0.88rem !important;
    margin: 0.15rem 0 !important;
}
.biodex-sample-note {
    color: var(--bd-moss);
    font-size: 0.86rem;
    margin: 0.2rem 0 0.35rem;
}

/* ── Stats ── */
.biodex-stat-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(90px, 1fr));
    gap: 0.55rem;
    margin: 0.65rem 0;
}
@media (max-width: 900px) {
    .biodex-stat-grid { grid-template-columns: repeat(2, 1fr); }
}
.biodex-stat {
    background: var(--bd-surface);
    -webkit-backdrop-filter: blur(8px);
    backdrop-filter: blur(8px);
    border: 1px solid var(--bd-border);
    border-radius: var(--bd-radius-sm);
    padding: 0.85rem 0.5rem;
    text-align: center;
    box-shadow: inset 0 1px 0 rgba(255, 240, 214, 0.05);
}
.biodex-stat-value {
    font-size: 1.7rem;
    font-weight: 800;
    line-height: 1.1;
    font-variant-numeric: tabular-nums;
}
.biodex-stat-label {
    font-size: 0.72rem;
    color: var(--bd-text-muted);
    margin-top: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.biodex-stat-total .biodex-stat-value { color: var(--bd-text); }
.biodex-stat-animal .biodex-stat-value { color: var(--bd-moss); }
.biodex-stat-person .biodex-stat-value { color: var(--bd-amber); }
.biodex-stat-vehicle .biodex-stat-value { color: var(--bd-terracotta); }
.biodex-stat-blank .biodex-stat-value { color: var(--bd-text-muted); }
.biodex-summary {
    border-left: 3px solid var(--bd-moss);
    padding: 0.5rem 0 0.5rem 0.85rem;
    margin: 0.4rem 0 0.65rem;
    color: var(--bd-text);
    font-size: 0.9rem;
    line-height: 1.45;
}
.biodex-warning {
    border-left: 3px solid var(--bd-amber);
    padding: 0.5rem 0 0.5rem 0.85rem;
    margin: 0.4rem 0;
    color: var(--bd-amber);
    font-size: 0.92rem;
}

/* ── Export row ── */
.biodex-export-row {
    gap: 0.5rem !important;
    margin-top: 0.35rem !important;
}
.biodex-export-label,
.biodex-export-label p {
    font-weight: 600 !important;
    color: var(--bd-text-muted) !important;
    font-size: 0.8rem !important;
    margin: 1rem 0 0.35rem !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

/* ── Footer ── */
.biodex-footer {
    text-align: center;
    color: var(--bd-text-muted);
    font-size: 0.85rem;
    margin-top: 1rem;
    padding: 1rem 0 0.5rem;
    border-top: 1px solid var(--bd-line);
}

/* ── Thin black borders on interactive elements ── */
.biodex-page button,
.biodex-page .gr-button,
.biodex-export-row button,
.gradio-container .tab-nav button {
    border: 1px solid var(--bd-line) !important;
}
.biodex-page input,
.biodex-page textarea,
.biodex-page select,
.biodex-page .gr-input,
.biodex-page .gr-box,
.gradio-container input[type="number"],
.gradio-container input[type="text"] {
    border: 1px solid var(--bd-line) !important;
}
.gradio-container .dataframe-wrap,
.gradio-container .table-wrap,
.gradio-container table {
    border: 1px solid var(--bd-line) !important;
}
.gradio-container th,
.gradio-container td,
.gradio-container .table-wrap button,
.gradio-container .thead button {
    border: 1px solid var(--bd-line) !important;
}
.gradio-container .checkbox-group,
.gradio-container .gr-check-radio {
    border: 1px solid var(--bd-line);
    border-radius: var(--bd-radius-sm);
    padding: 0.35rem 0.5rem;
}

/* ── Interactive widgets ── */
.gradio-container .upload-container,
.gradio-container .image-upload,
.gradio-container .file-preview {
    border: 1px solid var(--bd-line) !important;
    border-radius: var(--bd-radius-sm) !important;
    background: var(--bd-sand) !important;
}
.gradio-container .upload-container:hover,
.gradio-container .image-upload:hover {
    border-color: var(--bd-moss) !important;
}
.gradio-container .dataframe-wrap {
    border-radius: var(--bd-radius-sm) !important;
    overflow: hidden;
}
.gradio-container .accordion {
    border: none !important;
    border-radius: 0 !important;
    background: transparent !important;
    margin-top: 0.5rem !important;
}
.gradio-container footer {
    display: none !important;
}

/* ── Field device (rugged trail-cam review) ── */
.gradio-container.field-device,
.gradio-container:has(.field-device) {
    max-width: 1320px !important;
    padding: 0 1.25rem 2rem !important;
}
.field-device .gap {
    gap: 1rem !important;
}
.field-header {
    padding: 1.15rem 0 0.65rem;
    margin-bottom: 0.35rem;
}
.field-header-main {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
}
.field-title-main {
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1.35rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    color: var(--bd-text);
    text-transform: uppercase;
}
.field-title-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 5.3rem;
    height: 5.3rem;
    flex-shrink: 0;
    background: transparent;
    border: none;
    box-shadow: none;
    padding: 0;
}
.field-title-icon img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    display: block;
    border: none;
    outline: none;
    box-shadow: none;
    background: transparent;
}
.field-version {
    font-size: 0.68rem;
    font-weight: 600;
    color: var(--bd-earth);
    margin-left: auto;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 0.22rem 0.55rem;
    border-radius: 999px;
    background: rgba(139, 115, 85, 0.12);
    border: 1px solid rgba(139, 115, 85, 0.28);
}
.field-header-rule {
    height: 3px;
    margin-top: 0.85rem;
    border-radius: 999px;
    background: linear-gradient(
        90deg,
        transparent 0%,
        var(--bd-terracotta) 12%,
        var(--bd-moss) 50%,
        var(--bd-amber) 88%,
        transparent 100%
    );
    opacity: 0.85;
}

/* Batch review — solid glass panel (no backdrop blur — keeps images/tables sharp) */
.field-review-panel {
    display: flex !important;
    flex-direction: column !important;
    gap: 0.85rem !important;
    margin: 0.75rem 0 1rem !important;
    padding: 1.1rem 1.25rem !important;
    background: linear-gradient(180deg, #3a3226 0%, #2a2318 100%) !important;
    border: 1px solid var(--bd-border-strong) !important;
    border-radius: 16px !important;
    box-shadow: 0 12px 36px rgba(8, 6, 2, 0.45), inset 0 1px 0 rgba(255, 240, 214, 0.06) !important;
}
.field-review-panel .block,
.field-review-panel .form {
    background: transparent !important;
}
.field-review-panel .label-wrap span,
.field-review-panel .field-frame-title,
.field-review-panel .field-frame-title p {
    color: #f2ede2 !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    text-shadow: none !important;
}
.field-review-panel .field-table-wrap .dataframe-wrap,
.field-review-panel .field-detections-wrap .dataframe-wrap {
    background: rgba(20, 16, 11, 0.88) !important;
    border: 1px solid var(--bd-border-strong) !important;
}
.field-review-panel .field-table-wrap table,
.field-review-panel .field-detections-wrap table {
    color: #f2ede2 !important;
    font-size: 0.9rem !important;
}
.field-review-panel .field-table-wrap th,
.field-review-panel .field-detections-wrap th {
    background: rgba(38, 32, 22, 0.95) !important;
    color: var(--bd-earth) !important;
}
.field-review-panel .field-table-wrap td,
.field-review-panel .field-detections-wrap td {
    background: rgba(28, 23, 16, 0.75) !important;
    color: #f2ede2 !important;
}
.field-review-panel .field-image-panel .image-container,
.field-review-panel .field-image-panel .image-frame,
.field-review-panel .image-container,
.field-review-panel .image-frame {
    background: #0a0908 !important;
    border: 1px solid var(--bd-border-strong) !important;
    border-radius: 10px !important;
    min-height: 280px !important;
    max-height: 480px !important;
}
/* Keep image action icons (fullscreen/share) from breaking the glass panel layout */
.field-review-panel .image-container .icon-buttons,
.field-image-panel .image-container .icon-buttons {
    background: rgba(10, 9, 8, 0.55) !important;
    border-radius: 8px !important;
}

/* Sticky aggregate stats — always visible while scrolling */
.field-stats-strip {
    position: sticky;
    top: 0;
    z-index: 40;
    background: transparent;
    padding: 0.45rem 0;
    margin: 0.5rem 0 0.25rem;
}
.field-summary {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    gap: 0.65rem 2rem;
    padding: 1.1rem 1.4rem;
    background: linear-gradient(180deg, #3a3226 0%, #2a2318 100%);
    border: 1px solid var(--bd-border-strong);
    border-radius: 14px;
    box-shadow: 0 8px 26px rgba(8, 6, 2, 0.35), inset 0 1px 0 rgba(255, 240, 214, 0.05);
}
.field-summary-active {
    border-color: rgba(224, 169, 94, 0.45);
}
.field-summary-empty {
    color: var(--bd-text-muted);
    font-size: 0.92rem;
    font-weight: 500;
    letter-spacing: 0.02em;
    padding: 0.85rem 1.25rem;
    justify-content: center;
}
.field-stat {
    display: flex;
    flex-direction: column;
    min-width: 5rem;
}
.field-stat-primary .field-stat-val {
    font-size: 2.25rem;
}
.field-stat-val {
    font-size: 1.85rem;
    font-weight: 800;
    line-height: 1;
    color: var(--bd-text);
    font-variant-numeric: tabular-nums;
    text-shadow: 0 1px 8px rgba(0, 0, 0, 0.3);
}
.field-stat-animal .field-stat-val {
    color: var(--bd-moss);
}
.field-stat-lbl {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--bd-text-muted);
    margin-top: 0.3rem;
    font-weight: 600;
}
.field-stat-species {
    flex: 1 1 100%;
    min-width: 100%;
    padding-top: 0.35rem;
    border-top: 1px solid var(--bd-border);
    margin-top: 0.15rem;
}
.field-stat-species .field-stat-val {
    font-size: 0.9rem;
    font-weight: 600;
    line-height: 1.35;
}

/* Species toggle — always visible */
.field-species-bar {
    align-items: center !important;
    gap: 1rem !important;
    padding: 0.35rem 0 0.65rem !important;
    border-bottom: 1px solid var(--bd-border);
    margin-bottom: 0.25rem;
}
.field-species-bar .gr-checkbox {
    margin: 0 !important;
}
.field-species-bar .gr-checkbox label {
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    color: var(--bd-text) !important;
}
.field-species-status {
    flex: 1 1 auto !important;
    min-width: 0;
}
.field-species-pill {
    display: inline-block;
    padding: 0.4rem 0.75rem;
    border-radius: 6px;
    font-size: 0.8rem;
    line-height: 1.35;
    border: 1px solid var(--bd-border);
}
.field-species-pill-label {
    color: var(--bd-text);
}
.field-species-ok {
    background: rgba(134, 193, 147, 0.14);
    border-color: rgba(134, 193, 147, 0.5);
}
.field-species-ok .field-species-pill-label {
    color: var(--bd-moss);
    font-weight: 600;
}
.field-species-loading {
    background: rgba(224, 169, 94, 0.12);
    border-color: rgba(224, 169, 94, 0.45);
}
.field-species-warn {
    background: rgba(231, 184, 92, 0.12);
    border-color: rgba(231, 184, 92, 0.45);
}
.field-species-error {
    background: rgba(224, 145, 106, 0.14);
    border-color: rgba(224, 145, 106, 0.5);
}
.field-species-off {
    background: var(--bd-sand);
    color: var(--bd-text-muted);
}
.field-detections-wrap .dataframe-wrap {
    max-height: 200px;
    overflow-y: auto !important;
    border: 2px solid var(--bd-line) !important;
    border-radius: 6px !important;
}
.field-detections-wrap .label-wrap span {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: var(--bd-text-muted) !important;
}

/* AI review (BYOK LLM) */
.field-ai-review-bar {
    align-items: center !important;
    gap: 0.6rem !important;
    margin-top: 0.4rem;
}
.field-ai-review-hint {
    font-size: 0.78rem;
    color: #e0a95e !important;
    font-weight: 600;
    line-height: 1.3;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.65);
}
.field-ai-review {
    margin-top: 0.5rem;
    padding: 0.1rem 0.9rem;
    background: var(--bd-sand, #F5EDE3);
    border: 2px solid var(--bd-line);
    border-left: 4px solid var(--bd-moss, #4A7C59);
    border-radius: 8px;
}
.field-ai-review:empty {
    display: none;
}
.field-ai-review h3 {
    font-size: 0.82rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--bd-moss, #4A7C59) !important;
    margin: 0.7rem 0 0.2rem !important;
}
.field-ai-review sub {
    color: var(--bd-text-muted);
    font-size: 0.68rem;
}

/* Compact action row */
.field-action-bar {
    padding: 0.5rem 0 0.25rem;
    gap: 0.65rem !important;
    align-items: stretch !important;
}
.field-action-bar button {
    font-weight: 700 !important;
    letter-spacing: 0.03em !important;
    min-height: 2.75rem !important;
    border-radius: 6px !important;
}
.field-action-bar .gr-button-primary {
    min-width: 14rem;
    font-size: 1rem !important;
}
.field-status-line {
    font-size: 0.8rem !important;
    color: var(--bd-text-muted) !important;
    margin: 0 !important;
    padding: 0 0 0.5rem !important;
    letter-spacing: 0.02em;
}
.field-status-line p {
    margin: 0 !important;
}

/* Frame title above viewers */
.field-frame-title {
    font-size: 0.88rem !important;
    color: var(--bd-text) !important;
    margin: 0.75rem 0 0.35rem !important;
    padding: 0 !important;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.field-frame-title p {
    margin: 0 !important;
}
.field-frame-title strong {
    color: var(--bd-moss);
    font-weight: 700;
}

/* Dominant side-by-side viewers */
.field-viewer-row {
    gap: 1rem !important;
    margin: 0.25rem 0 1rem !important;
}
.field-viewer-row > .block,
.field-viewer-img .block {
    flex: 1 1 50% !important;
}
.field-viewer-img .image-container,
.field-viewer-img img,
.field-image-panel .image-container,
.field-image-panel img {
    border-radius: 4px !important;
    border: 2px solid var(--bd-line) !important;
    background: #141412 !important;
}
.field-viewer-img .image-frame,
.field-image-panel .image-frame {
    min-height: 0 !important;
    max-height: 480px !important;
}
.field-viewer-img .empty,
.field-image-panel .empty {
    min-height: 120px !important;
    max-height: 160px !important;
}
.field-viewer-img .label-wrap,
.field-image-panel .label-wrap {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: var(--bd-text-muted) !important;
    margin-bottom: 0.35rem !important;
}

/* Results table — scannable, compact */
.biodex-page .field-table-wrap {
    margin-top: 0.5rem;
}
.biodex-page .field-table-wrap .label-wrap span {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: var(--bd-text-muted) !important;
}
.biodex-page .field-table-wrap .dataframe-wrap {
    max-height: 240px;
    overflow-y: auto !important;
    border: 2px solid var(--bd-line) !important;
    border-radius: 6px !important;
}
.biodex-page .field-table-wrap table {
    font-size: 0.82rem !important;
}
/* Hide dataframe copy/fullscreen toolbar icons — they render as empty boxes */
.biodex-page .table-container .toolbar {
    display: none !important;
}

.biodex-page .field-table-wrap th {
    background: var(--bd-sage-deep) !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.05em !important;
}

/* Batch accordions — warm brown labels (Folder upload, Export, Spot check) */
.biodex-page .block.field-batch-accordion,
.biodex-page .block.field-batch-accordion.padded,
.biodex-page .field-batch-accordion,
.biodex-page .accordion,
.field-device .accordion {
    background: linear-gradient(180deg, #3d2e1f 0%, #2a1f14 100%) !important;
    border: 1px solid rgba(201, 152, 88, 0.55) !important;
    border-radius: 10px !important;
    margin-top: 0.55rem !important;
    padding: 0.1rem 0.65rem !important;
    box-shadow: 0 4px 14px rgba(8, 6, 2, 0.45) !important;
}
.biodex-page .block.field-batch-accordion .label-wrap {
    background: linear-gradient(180deg, #4a3826 0%, #3d2e1f 100%) !important;
    border-radius: 8px !important;
    width: 100% !important;
}
.biodex-page .field-batch-accordion > .label-wrap,
.biodex-page .field-batch-accordion .label-wrap,
.biodex-page .accordion > .label-wrap,
.biodex-page .accordion .label-wrap,
.field-device .accordion > .label-wrap,
.field-device .accordion .label-wrap {
    opacity: 1 !important;
    background: transparent !important;
    padding: 0.55rem 0.25rem !important;
    border: none !important;
}
.biodex-page .field-batch-accordion .label-wrap span,
.biodex-page .field-batch-accordion .label-wrap p,
.biodex-page .field-batch-accordion button,
.biodex-page .field-batch-accordion summary,
.biodex-page .accordion .label-wrap span,
.biodex-page .accordion .label-wrap p,
.biodex-page .accordion > button,
.biodex-page .accordion summary,
.field-device .accordion .label-wrap span,
.field-device .accordion .label-wrap p,
.field-device .accordion > button,
.field-device .accordion summary {
    color: #e0a95e !important;
    -webkit-text-fill-color: #e0a95e !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    text-transform: none !important;
    letter-spacing: 0.02em !important;
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.75) !important;
}
.biodex-page .field-batch-accordion:hover .label-wrap span,
.biodex-page .accordion:hover .label-wrap span,
.field-device .accordion:hover .label-wrap span {
    color: #f0c070 !important;
    -webkit-text-fill-color: #f0c070 !important;
}
.biodex-page .field-batch-accordion svg,
.biodex-page .accordion svg,
.field-device .accordion svg {
    color: #e0a95e !important;
    stroke: #e0a95e !important;
    fill: #e0a95e !important;
}
.field-device .accordion .accordion-content,
.field-device .accordion > .wrap,
.biodex-page .field-batch-accordion .accordion-content,
.biodex-page .field-batch-accordion > .wrap {
    background: #1e1812 !important;
    border-radius: 0 0 8px 8px !important;
    padding: 0.75rem 0.85rem 0.9rem !important;
    margin-top: 0.15rem !important;
}
.field-export-row {
    padding: 0.25rem 0 0.5rem;
    gap: 0.5rem !important;
}
.field-review-label {
    font-size: 0.85rem;
    color: var(--bd-text-muted);
    margin: 0.25rem 0 0.5rem;
}
.field-review-label strong {
    color: var(--bd-text);
}
.field-footer {
    text-align: center;
    color: var(--bd-text-muted);
    padding: 1.5rem 0.5rem 0.35rem;
    margin-top: 1.35rem;
    border-top: 1px solid var(--bd-border);
    background: linear-gradient(180deg, transparent 0%, rgba(46, 38, 27, 0.3) 100%);
    border-radius: 0 0 12px 12px;
}
.field-footer-tagline {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.5rem 0.65rem;
    margin: 0 0 1.15rem;
}
.field-footer-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.02em;
    color: var(--bd-text);
    padding: 0.3rem 0.7rem 0.3rem 0.52rem;
    border-radius: 999px;
    background: rgba(54, 44, 31, 0.5);
    -webkit-backdrop-filter: blur(8px);
    backdrop-filter: blur(8px);
    border: 1px solid var(--bd-border);
    box-shadow: inset 0 1px 0 rgba(255, 240, 214, 0.05);
}
.field-footer-badge-icon {
    display: inline-flex;
    color: var(--bd-moss);
}
.field-footer-badge-icon svg {
    width: 0.95rem;
    height: 0.95rem;
}
.field-footer-actions {
    display: flex !important;
    justify-content: center !important;
    margin: 0 !important;
    padding: 0 !important;
}
.field-footer-actions .prose,
.field-footer-actions .html-container {
    width: 100%;
    margin: 0 !important;
    padding: 0 !important;
}
.field-footer-chips {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.55rem;
    width: 100%;
}
.field-footer-chip {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
    font: inherit;
    font-size: 0.76rem;
    font-weight: 500;
    line-height: 1;
    color: var(--bd-text-muted);
    text-decoration: none;
    cursor: pointer;
    white-space: nowrap;
    padding: 0.42rem 0.8rem 0.42rem 0.58rem;
    border-radius: 999px;
    background: var(--bd-sand);
    border: 1px solid var(--bd-border);
    box-shadow: 0 1px 4px rgba(44, 51, 40, 0.08);
    transition: color 0.15s ease, border-color 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;
}
button.field-footer-chip {
    appearance: none;
}
.field-footer-chip:hover {
    color: var(--bd-moss);
    border-color: var(--bd-moss);
    box-shadow: 0 2px 8px rgba(74, 124, 89, 0.18);
    transform: translateY(-1px);
}
.field-footer-chip-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.35rem;
    height: 1.35rem;
    border-radius: 50%;
    background: rgba(134, 193, 147, 0.16);
}
.field-footer-chip-icon svg {
    width: 0.85rem;
    height: 0.85rem;
}
.field-footer-section {
    text-align: center;
    margin-top: 1.35rem;
    padding: 1.5rem 0.5rem 0.35rem;
    border-top: 1px solid var(--bd-border);
    background: linear-gradient(180deg, transparent 0%, rgba(46, 38, 27, 0.3) 100%);
    border-radius: 0 0 12px 12px;
}
.field-footer-section .field-footer-tagline {
    margin-bottom: 1.15rem;
}
.field-api-toggle {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0.4rem !important;
    width: auto !important;
    min-width: 0 !important;
    flex: 0 0 auto !important;
    font: inherit !important;
    font-size: 0.76rem !important;
    font-weight: 500 !important;
    line-height: 1 !important;
    color: var(--bd-text-muted) !important;
    white-space: nowrap !important;
    padding: 0.42rem 0.8rem 0.42rem 0.58rem !important;
    border-radius: 999px !important;
    background: var(--bd-sand) !important;
    border: 1px solid var(--bd-border) !important;
    box-shadow: 0 1px 4px rgba(44, 51, 40, 0.08) !important;
}
.field-api-toggle::before {
    content: "</>";
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.35rem;
    height: 1.35rem;
    border-radius: 50%;
    background: rgba(134, 193, 147, 0.16);
    color: var(--bd-moss);
    font-size: 0.62rem;
    font-weight: 700;
}
.field-api-toggle:hover {
    color: var(--bd-moss) !important;
    border-color: var(--bd-moss) !important;
}
.field-footer-actions > .block,
.field-footer-actions > .column {
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: 0 !important;
}
.field-api-menu {
    max-width: 380px;
    margin: 0 auto 0.65rem !important;
    padding: 0.85rem 0.95rem 0.9rem !important;
    background: linear-gradient(180deg, rgba(46, 38, 27, 0.92) 0%, rgba(31, 26, 18, 0.94) 100%) !important;
    -webkit-backdrop-filter: blur(18px) saturate(130%) !important;
    backdrop-filter: blur(18px) saturate(130%) !important;
    border: 1px solid var(--bd-border-strong) !important;
    border-radius: 14px !important;
    box-shadow: 0 18px 44px rgba(8, 6, 2, 0.5), inset 0 1px 0 rgba(255, 240, 214, 0.06) !important;
    text-align: left !important;
    gap: 0.35rem !important;
}
.field-api-menu .gap {
    gap: 0.35rem !important;
}
.field-api-menu-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 0.5rem;
    margin-bottom: 0.35rem;
    padding-bottom: 0.45rem;
    border-bottom: 1px solid var(--bd-border);
}
.field-api-menu-title {
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--bd-text);
}
.field-api-menu-sub {
    font-size: 0.62rem;
    color: var(--bd-text-muted);
    white-space: nowrap;
}
.field-api-menu .block,
.field-api-menu .form,
.field-api-menu .html-container {
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}
.field-api-menu .label-wrap {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 0 0.15rem !important;
    min-height: 0 !important;
    margin: 0 !important;
}
.field-api-menu .label-wrap span,
.field-api-menu label span {
    display: block;
    font-size: 0.62rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--bd-text-muted) !important;
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    line-height: 1.2 !important;
}
.field-api-menu input,
.field-api-menu textarea,
.field-api-menu .wrap,
.field-api-menu .single-select {
    min-height: 2rem !important;
    background: var(--bd-sand) !important;
    color: var(--bd-text) !important;
    font-size: 0.8rem !important;
    border-radius: 6px !important;
}
.field-api-menu-grid {
    gap: 0.45rem !important;
    align-items: flex-end !important;
}
.field-api-menu-grid > .block,
.field-api-menu-grid > .column {
    flex: 1 1 0 !important;
    min-width: 0 !important;
}
.field-api-menu-actions {
    margin-top: 0.25rem !important;
    gap: 0.35rem !important;
    flex-wrap: nowrap !important;
}
.field-api-menu-actions > .block,
.field-api-menu-actions > .column {
    flex: 1 1 0 !important;
    min-width: 0 !important;
}
.field-api-menu-actions button {
    width: 100% !important;
    min-width: 0 !important;
    min-height: 2rem !important;
    padding: 0.3rem 0.45rem !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
}
.field-api-status {
    margin: 0.15rem 0 0 !important;
    min-height: 1rem;
}
.field-api-status p {
    margin: 0 !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    color: var(--bd-moss) !important;
    line-height: 1.3 !important;
}
.field-footer-chip-icon-api svg {
    width: 0.85rem;
    height: 0.85rem;
}
.field-footer-chip-icon-gradio {
    color: #f97700;
    background: rgba(249, 119, 0, 0.1);
}
.field-footer-chip-icon-settings {
    color: var(--bd-earth);
    background: rgba(139, 115, 85, 0.12);
}
"""

DARK_CSS = """
.biodex-dark {
    --bd-cream: #1a1f1c;
    --bd-surface: #232923;
    --bd-sage: #2a322c;
    --bd-sage-deep: #1e2420;
    --bd-sand: #2e3630;
    --bd-tan: #353d37;
    --bd-border: #4a554e;
    --bd-moss: #6aab7a;
    --bd-moss-hover: #5a9568;
    --bd-earth: #a89070;
    --bd-text: #e8ebe9;
    --bd-line: #5a6560;
    --bd-text-muted: #a8b0ab;
}
.biodex-dark.gradio-container,
.biodex-dark .gradio-container {
    background: var(--bd-cream) !important;
    color-scheme: dark !important;
}
@media (max-width: 640px) {
    .gradio-container.field-device {
        padding: 0 0.5rem 1rem !important;
    }
    .field-action-bar {
        flex-direction: column !important;
    }
    .field-viewer-row {
        flex-direction: column !important;
    }
}
"""


def dark_mode_css() -> str:
    """Return dark mode and mobile CSS overrides."""
    return DARK_CSS


# Launch background. Prefer ``ui/tree_of_life_background.avif``, then ``.jpg``.
# Inlined as a base64 data URI so it works locally, in Docker, and on deploy.
_TREE_OVERLAY = "rgba(26, 18, 8, 0.40)"
_UI_DIR = Path(__file__).resolve().parent
_BACKGROUND_CANDIDATES: tuple[tuple[Path, str], ...] = (
    (_UI_DIR / "tree_of_life_background.avif", "image/avif"),
    (_UI_DIR / "tree_of_life_background.jpg", "image/jpeg"),
)


def _resolve_tree_background() -> tuple[Path, str] | None:
    for path, mime in _BACKGROUND_CANDIDATES:
        if path.is_file():
            return path, mime
    return None


def tree_background_css() -> str:
    """Return CSS that paints the Tree of Life background, or '' if unavailable."""
    resolved = _resolve_tree_background()
    if resolved is None:
        return ""
    path, mime = resolved
    try:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    except OSError:
        return ""
    return (
        ".biodex-page::before {\n"
        "    background-image:\n"
        f"        linear-gradient({_TREE_OVERLAY}, {_TREE_OVERLAY}),\n"
        f'        url("data:{mime};base64,{encoded}");\n'
        "}\n"
    )
