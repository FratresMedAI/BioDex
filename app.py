"""
BioDex — Local AI for Wildlife Camera Traps (v0.2)

Gradio web UI for MegaDetector v5a detection and optional SpeciesNet classification.
All inference runs locally; no cloud API calls during analysis.
"""

from __future__ import annotations

import traceback

import gradio as gr
import pandas as pd
from PIL import Image

from core.detector import run_analysis
from core.exports import detections_to_csv, export_json, save_annotated_image
from core.types import BIODEX_VERSION, AnalysisResult
from core.visualization import draw_detections

CUSTOM_CSS = """
.biodex-shell {
    max-width: 1200px;
    margin: 0 auto;
}
.biodex-header {
    text-align: center;
    margin-bottom: 1.25rem;
    padding: 1.25rem 1rem 0.5rem;
}
.biodex-header h1 {
    margin: 0 0 0.35rem 0;
    font-weight: 700;
    font-size: 2rem;
}
.biodex-tagline {
    color: #546E7A;
    font-size: 1.05rem;
    margin: 0.35rem 0 0.75rem;
}
.biodex-badge-row {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.biodex-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.biodex-badge-version {
    background: #E8F5E9;
    color: #1B5E20;
}
.biodex-badge-privacy {
    background: #ECEFF1;
    color: #455A64;
}
.biodex-panel {
    background: #FAFAFA;
    border: 1px solid #ECEFF1;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.biodex-footer {
    text-align: center;
    color: #78909C;
    font-size: 0.9rem;
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid #ECEFF1;
}
.biodex-stat-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(120px, 1fr));
    gap: 0.75rem;
    margin: 1rem 0;
}
@media (max-width: 900px) {
    .biodex-stat-grid {
        grid-template-columns: repeat(2, minmax(120px, 1fr));
    }
}
.biodex-stat {
    background: #FFFFFF;
    border: 1px solid #E8F5E9;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    text-align: center;
    box-shadow: 0 1px 2px rgba(46, 125, 50, 0.08);
}
.biodex-stat-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #2E7D32;
    line-height: 1.1;
}
.biodex-stat-label {
    font-size: 0.82rem;
    color: #546E7A;
    margin-top: 0.25rem;
}
.biodex-summary {
    background: #F1F8E9;
    border-left: 4px solid #2E7D32;
    border-radius: 8px;
    padding: 0.85rem 1rem;
    margin: 0.75rem 0 1rem;
    color: #37474F;
}
"""

HOW_IT_WORKS = """
### How BioDex works

BioDex runs entirely on your computer. Your images are never uploaded to a cloud API.

**Step 1 — Detection (MegaDetector v5a)**  
[MegaDetector](https://github.com/agentmorris/MegaDetector) finds animals, people, and vehicles in camera trap images and returns bounding boxes with confidence scores.

**Step 2 — Species classification (optional)**  
When enabled, BioDex crops each animal detection and runs [SpeciesNet](https://github.com/google/cameratrapai) locally to suggest likely species. SpeciesNet covers ~2,000 taxa trained on diverse camera trap data, but accuracy varies by region.

**Blank images:** An image is treated as a **blank** when no animal, person, or vehicle passes your confidence threshold.

**First run:** Model weights download once (MegaDetector ~280 MB; SpeciesNet ~100 MB if enabled), then analysis works offline.
"""

RESULTS_COLUMNS = [
    "ID",
    "Category",
    "Confidence",
    "Species",
    "Species Conf",
    "BBox",
]


def _format_bbox(bbox: list[float]) -> str:
    xmin, ymin, width, height = bbox
    return f"{xmin:.3f},{ymin:.3f},{width:.3f},{height:.3f}"


def _build_results_dataframe(result: AnalysisResult) -> pd.DataFrame:
    rows = []
    for detection in result.detections:
        species_label = detection.species.label if detection.species else ""
        species_conf = (
            f"{detection.species.confidence:.3f}" if detection.species else ""
        )
        rows.append(
            [
                detection.detection_id,
                detection.category.title(),
                f"{detection.confidence:.3f}",
                species_label,
                species_conf,
                _format_bbox(detection.bbox),
            ]
        )
    return pd.DataFrame(rows, columns=RESULTS_COLUMNS)


def _format_stats_markdown(result: AnalysisResult) -> str:
    blank_label = "Yes" if result.is_blank else "No"
    return f"""
<div class="biodex-stat-grid">
  <div class="biodex-stat">
    <div class="biodex-stat-value">{result.total}</div>
    <div class="biodex-stat-label">Total detections</div>
  </div>
  <div class="biodex-stat">
    <div class="biodex-stat-value">{result.animal_count}</div>
    <div class="biodex-stat-label">Animals</div>
  </div>
  <div class="biodex-stat">
    <div class="biodex-stat-value">{result.person_count}</div>
    <div class="biodex-stat-label">People</div>
  </div>
  <div class="biodex-stat">
    <div class="biodex-stat-value">{result.vehicle_count}</div>
    <div class="biodex-stat-label">Vehicles</div>
  </div>
  <div class="biodex-stat">
    <div class="biodex-stat-value">{blank_label}</div>
    <div class="biodex-stat-label">Blank image</div>
  </div>
</div>

<div class="biodex-summary">{result.summary}</div>
"""


def analyze_image(
    image: Image.Image | None,
    threshold: float,
    classify_species: bool,
):
    """
    Main analysis handler: detect, optionally classify species, annotate, export.
    """
    if image is None:
        raise gr.Error("Please upload a camera trap image (JPG or PNG) first.")

    try:
        if not isinstance(image, Image.Image):
            image = Image.open(image)

        result = run_analysis(
            image,
            threshold=threshold,
            classify_species=classify_species,
            filename="upload",
        )
        annotated = draw_detections(image, result.detections)
        stats_md = _format_stats_markdown(result)
        results_df = _build_results_dataframe(result)

        annotated_path = save_annotated_image(annotated)
        csv_path = detections_to_csv(result)
        json_path = export_json(result)

        return (
            image,
            annotated,
            stats_md,
            results_df,
            gr.update(value=annotated_path, visible=True),
            gr.update(value=csv_path, visible=True),
            gr.update(value=json_path, visible=True),
        )

    except gr.Error:
        raise
    except ValueError as exc:
        raise gr.Error(str(exc)) from exc
    except Exception as exc:
        tb = traceback.format_exc()
        raise gr.Error(
            f"Analysis failed: {exc}\n\n"
            "If this is your first run, model weights may still be downloading. "
            "Check your internet connection and try again.\n\n"
            f"Details:\n```\n{tb}\n```"
        ) from exc


APP_THEME = gr.themes.Soft(
    primary_hue="green",
    secondary_hue="emerald",
    neutral_hue="gray",
)


def build_app() -> gr.Blocks:
    """Construct and return the Gradio Blocks application."""
    with gr.Blocks(title="BioDex") as demo:
        gr.HTML(
            f"""
            <div class="biodex-shell">
              <div class="biodex-header">
                <h1>BioDex — Local AI for Wildlife Camera Traps</h1>
                <p class="biodex-tagline">
                  Detect wildlife, filter blanks, identify species, and export results — 100% on your machine.
                </p>
                <div class="biodex-badge-row">
                  <span class="biodex-badge biodex-badge-version">v{BIODEX_VERSION}</span>
                  <span class="biodex-badge biodex-badge-privacy">Local only • Privacy-first</span>
                </div>
              </div>
            </div>
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                with gr.Group():
                    input_image = gr.Image(
                        label="Upload camera trap image",
                        type="pil",
                        sources=["upload"],
                        height=320,
                    )
                    threshold = gr.Slider(
                        minimum=0.05,
                        maximum=0.95,
                        value=0.25,
                        step=0.05,
                        label="Confidence threshold",
                        info="Higher = fewer, more confident detections",
                    )
                    classify_species = gr.Checkbox(
                        value=False,
                        label="Enable species classification",
                        info="Runs SpeciesNet on animal crops (~5–15s on CPU; downloads weights on first use)",
                    )
                    analyze_btn = gr.Button("Analyze Image", variant="primary", size="lg")

            with gr.Column(scale=1):
                gr.Markdown(
                    """
                    **Workflow**
                    1. Upload a JPG or PNG camera trap image
                    2. Adjust confidence threshold
                    3. Optionally enable species classification
                    4. Click **Analyze Image** and export results
                    """
                )

        with gr.Row():
            with gr.Column():
                original_out = gr.Image(
                    label="Original",
                    type="pil",
                    interactive=False,
                    height=420,
                )
            with gr.Column():
                annotated_out = gr.Image(
                    label="Annotated detections",
                    type="pil",
                    interactive=False,
                    height=420,
                )

        stats_panel = gr.Markdown(label="Analysis summary")
        results_table = gr.Dataframe(
            headers=RESULTS_COLUMNS,
            label="Detections",
            interactive=False,
            wrap=True,
        )

        gr.Markdown("### Export results")
        with gr.Row():
            download_image = gr.File(label="Annotated image (PNG)", visible=False)
            download_csv = gr.File(label="Detections (CSV)", visible=False)
            download_json = gr.File(label="Results (JSON)", visible=False)

        with gr.Accordion("How it works", open=False):
            gr.Markdown(HOW_IT_WORKS)

        gr.HTML(
            """
            <div class="biodex-footer">
                Local only &nbsp;•&nbsp; Privacy-first &nbsp;•&nbsp; Open source
            </div>
            """
        )

        analyze_btn.click(
            fn=analyze_image,
            inputs=[input_image, threshold, classify_species],
            outputs=[
                original_out,
                annotated_out,
                stats_panel,
                results_table,
                download_image,
                download_csv,
                download_json,
            ],
            show_progress="full",
        )

    return demo


if __name__ == "__main__":
    app = build_app()
    app.launch(theme=APP_THEME, css=CUSTOM_CSS)
