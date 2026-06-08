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
    padding: 1.5rem 0 1rem;
    border-bottom: 2px solid var(--bd-line);
    margin-bottom: 0.25rem;
}
.field-header-main {
    display: flex;
    align-items: baseline;
    gap: 0.75rem;
    flex-wrap: wrap;
}
.field-brand {
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    color: var(--bd-text);
    text-transform: uppercase;
}
.field-title {
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--bd-earth);
}
.field-version {
    font-size: 0.72rem;
    color: var(--bd-text-muted);
    margin-left: auto;
    letter-spacing: 0.04em;
}
.field-tagline {
    margin: 0.45rem 0 0;
    font-size: 0.84rem;
    color: var(--bd-text-muted);
    letter-spacing: 0.02em;
}

/* Sticky aggregate stats — always visible while scrolling */
.field-stats-strip {
    position: sticky;
    top: 0;
    z-index: 40;
    background: var(--bd-cream);
    padding: 0.35rem 0;
    margin: 0.5rem 0 0.25rem;
}
.field-summary {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    gap: 0.65rem 2rem;
    padding: 1rem 1.25rem;
    background: linear-gradient(180deg, #E8E2D6 0%, var(--bd-sand) 100%);
    border: 2px solid var(--bd-line);
    border-radius: 6px;
    box-shadow: 0 1px 0 rgba(44, 51, 40, 0.06);
}
.field-summary-active {
    border-color: var(--bd-earth);
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
    font-size: 1.85rem;
}
.field-stat-val {
    font-size: 1.55rem;
    font-weight: 800;
    line-height: 1;
    color: var(--bd-text);
    font-variant-numeric: tabular-nums;
}
.field-stat-animal .field-stat-val {
    color: var(--bd-moss);
}
.field-stat-lbl {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--bd-text-muted);
    margin-top: 0.25rem;
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
    background: #e8f0ea;
    border-color: var(--bd-moss);
}
.field-species-ok .field-species-pill-label {
    color: var(--bd-moss);
    font-weight: 600;
}
.field-species-loading {
    background: #f5f0e4;
    border-color: var(--bd-earth);
}
.field-species-warn {
    background: #faf4ec;
    border-color: var(--bd-amber);
}
.field-species-error {
    background: #faf0ee;
    border-color: var(--bd-terracotta);
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
.biodex-page .field-table-wrap th {
    background: var(--bd-sage-deep) !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.05em !important;
}

/* Collapsed sections — low visual weight */
.field-device .accordion {
    border-top: 1px solid var(--bd-border) !important;
    margin-top: 0.75rem !important;
}
.field-device .accordion > .label-wrap {
    opacity: 0.85;
}
.field-device .accordion > .label-wrap span {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: var(--bd-text-muted) !important;
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
    font-size: 0.68rem;
    color: var(--bd-text-muted);
    padding: 2rem 0 0.5rem;
    border-top: 1px solid var(--bd-border);
    margin-top: 1.5rem;
    opacity: 0.7;
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
