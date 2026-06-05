"""BioDex Gradio UI theme and custom styles."""

import gradio as gr

# Nature-inspired palette — warm sand & tan (mirrored in CSS :root)
_BD_CREAM = "#E8DFD0"
_BD_SURFACE = "#F0E8DC"
_BD_SAGE = "#E4DDD0"
_BD_SAND = "#F5EDE3"
_BD_BORDER = "#C9BFB0"
_BD_MOSS = "#4A7C59"
_BD_MOSS_HOVER = "#3D6849"
_BD_EARTH = "#8B7355"
_BD_TEXT = "#2C3328"
_BD_TEXT_MUTED = "#5C6658"

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
        button_primary_text_color=_BD_SAND,
        button_primary_text_color_dark=_BD_SAND,
        button_secondary_background_fill=_BD_SAND,
        button_secondary_background_fill_dark=_BD_SAND,
        button_secondary_background_fill_hover=_BD_SAGE,
        button_secondary_background_fill_hover_dark=_BD_SAGE,
        button_secondary_text_color=_BD_MOSS,
        button_secondary_text_color_dark=_BD_MOSS,
        button_secondary_border_color=_BD_TEXT,
        button_secondary_border_color_dark=_BD_TEXT,
        input_background_fill=_BD_SAND,
        input_background_fill_dark=_BD_SAND,
        input_border_color=_BD_TEXT,
        input_border_color_dark=_BD_TEXT,
        slider_color=_BD_MOSS,
        slider_color_dark=_BD_MOSS,
        checkbox_background_color=_BD_CREAM,
        checkbox_background_color_dark=_BD_CREAM,
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
    --bd-cream: #E8DFD0;
    --bd-surface: #F0E8DC;
    --bd-sage: #E4DDD0;
    --bd-sage-deep: #D8CFC0;
    --bd-sand: #F5EDE3;
    --bd-tan: #E2D8C8;
    --bd-border: #C9BFB0;
    --bd-moss: #4A7C59;
    --bd-moss-hover: #3D6849;
    --bd-earth: #8B7355;
    --bd-text: #2C3328;
    --bd-line: #2C3328;
    --bd-text-muted: #5C6658;
    --bd-amber: #B8860B;
    --bd-terracotta: #C4705A;
    --bd-radius-sm: 10px;
}

/* Page shell */
.gradio-container,
.dark .gradio-container {
    color-scheme: light !important;
    background: var(--bd-cream) !important;
    max-width: 960px !important;
    margin: 0 auto !important;
    font-family: "Segoe UI", system-ui, -apple-system, sans-serif !important;
}
.gradio-container .main,
.gradio-container .wrap,
.gradio-container .contain,
.dark .gradio-container .main,
.dark .gradio-container .wrap {
    background: var(--bd-cream) !important;
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

/* ── Header (single soft card) ── */
.biodex-header {
    text-align: center;
    margin-bottom: 0.25rem;
    padding: 1.5rem 1rem 1.15rem;
    background: linear-gradient(180deg, var(--bd-sage) 0%, var(--bd-cream) 85%);
    border-radius: var(--bd-radius-sm);
}
.biodex-header h1 {
    margin: 0 0 0.25rem 0;
    font-family: Georgia, "Times New Roman", serif;
    font-weight: 700;
    font-size: 1.85rem;
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
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
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
    font-size: 0.88rem;
    line-height: 1.45;
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
    font-size: 1.05rem !important;
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
    font-weight: 500 !important;
    padding: 0.55rem 1rem !important;
    box-shadow: none !important;
}
.biodex-tabs button.selected,
.biodex-tabs .tab-nav button.selected {
    color: var(--bd-moss) !important;
    font-weight: 700 !important;
    border-bottom-color: var(--bd-moss) !important;
    background: transparent !important;
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
    background: var(--bd-sand);
    border: 1px solid var(--bd-line);
    border-radius: var(--bd-radius-sm);
    padding: 0.65rem 0.5rem;
    text-align: center;
}
.biodex-stat-value {
    font-size: 1.35rem;
    font-weight: 700;
    line-height: 1.1;
}
.biodex-stat-label {
    font-size: 0.72rem;
    color: var(--bd-text-muted);
    margin-top: 0.2rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
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
    color: #6B5A3E;
    font-size: 0.9rem;
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
    border-top: 1px solid var(--bd-line) !important;
    border-radius: 0 !important;
    background: transparent !important;
    margin-top: 0.5rem !important;
}
.gradio-container footer {
    opacity: 0.65;
}

/* ── Field review (minimal) ── */
.gradio-container {
    max-width: 1180px !important;
}
.field-header {
    padding: 1.25rem 0 0.75rem;
    border-bottom: 1px solid var(--bd-line);
    margin-bottom: 0.5rem;
}
.field-header-main {
    display: flex;
    align-items: baseline;
    gap: 0.65rem;
    flex-wrap: wrap;
}
.field-brand {
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: var(--bd-text);
    text-transform: uppercase;
}
.field-title {
    font-size: 1.1rem;
    font-weight: 500;
    color: var(--bd-earth);
}
.field-version {
    font-size: 0.75rem;
    color: var(--bd-text-muted);
    margin-left: auto;
}
.field-tagline {
    margin: 0.35rem 0 0;
    font-size: 0.88rem;
    color: var(--bd-text-muted);
}
.field-action-bar {
    padding: 0.75rem 0;
    gap: 0.5rem;
}
.field-action-bar .gr-button-primary {
    min-width: 10rem;
}
.field-summary {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem 1.25rem;
    padding: 0.85rem 0;
    border-top: 1px solid var(--bd-border);
    border-bottom: 1px solid var(--bd-border);
    margin: 0.25rem 0 0.75rem;
}
.field-summary-empty {
    color: var(--bd-text-muted);
    font-size: 0.9rem;
    padding: 0.5rem 0;
}
.field-stat {
    display: flex;
    flex-direction: column;
    min-width: 4.5rem;
}
.field-stat-val {
    font-size: 1.45rem;
    font-weight: 700;
    line-height: 1.1;
    color: var(--bd-text);
    font-variant-numeric: tabular-nums;
}
.field-stat-animal .field-stat-val {
    color: var(--bd-moss);
}
.field-stat-lbl {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--bd-text-muted);
    margin-top: 0.15rem;
}
.field-stat-species {
    flex: 1 1 100%;
    min-width: 100%;
}
.field-stat-species .field-stat-val {
    font-size: 0.95rem;
    font-weight: 600;
}
.field-review-label {
    font-size: 0.85rem;
    color: var(--bd-text-muted);
    margin: 0.25rem 0 0.5rem;
}
.field-review-label strong {
    color: var(--bd-text);
}
.field-image-panel .image-container,
.field-image-panel img {
    border-radius: 4px !important;
    border: 1px solid var(--bd-line) !important;
    background: #1a1a18 !important;
}
.field-image-panel .image-frame {
    min-height: 420px !important;
}
.field-export-row {
    padding: 0.5rem 0 0.75rem;
    border-top: 1px solid var(--bd-border);
}
.field-footer {
    text-align: center;
    font-size: 0.72rem;
    color: var(--bd-text-muted);
    padding: 1.5rem 0 0.5rem;
    border-top: 1px solid var(--bd-border);
    margin-top: 1rem;
}
.biodex-page .field-table-wrap .dataframe-wrap {
    max-height: 220px;
    overflow-y: auto !important;
}
"""
