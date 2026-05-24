"""
BioDex — Local AI for Wildlife Camera Traps

Gradio web UI for single-image MegaDetector v5a analysis.
All inference runs locally; no cloud API calls during analysis.
"""

from __future__ import annotations

import traceback

import gradio as gr
from PIL import Image

from core.detector import get_category_label, run_detection
from core.exports import detections_to_csv, save_annotated_image
from core.visualization import draw_detections

CUSTOM_CSS = """
.biodex-header {
    text-align: center;
    margin-bottom: 0.5rem;
}
.biodex-header h1 {
    margin-bottom: 0.25rem;
    font-weight: 700;
}
.biodex-tagline {
    color: #546E7A;
    font-size: 1.05rem;
    margin-top: 0;
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
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 0.75rem;
    margin: 1rem 0;
}
.biodex-stat {
    background: #F1F8E9;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    text-align: center;
}
.biodex-stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #2E7D32;
}
.biodex-stat-label {
    font-size: 0.85rem;
    color: #546E7A;
}
"""

HOW_IT_WORKS = """
### How BioDex works

BioDex uses **[MegaDetector v5a](https://github.com/agentmorris/MegaDetector)** (MDV5A), a widely used
open-source object detector trained on millions of camera trap images.

**What it detects (3 classes):**
- **Animal** — wildlife in the frame
- **Person** — humans (useful for separating human-triggered images)
- **Vehicle** — cars, trucks, bicycles, etc.

**Blank images:** MegaDetector does not have a separate "blank" class. An image is treated as a
**blank** when no animal, person, or vehicle is found above your confidence threshold.

**Privacy:** Images are processed entirely on your machine. The model weights download once on
first use (~200 MB); after that, analysis works offline.

**Note:** MegaDetector finds *where* animals are — it does not identify species. Species
classification is on the [roadmap](docs/roadmap.md).
"""


def _format_top_detections(detections: list, limit: int = 10) -> str:
    """Build a markdown table of top detections sorted by confidence."""
    if not detections:
        return "_No detections above threshold._"

    sorted_dets = sorted(detections, key=lambda d: d.get("conf", 0.0), reverse=True)[:limit]
    lines = ["| # | Class | Confidence |", "|---|-------|------------|"]
    for i, det in enumerate(sorted_dets, start=1):
        label = get_category_label(str(det.get("category", ""))).title()
        conf = float(det.get("conf", 0.0))
        lines.append(f"| {i} | {label} | {conf:.3f} |")
    return "\n".join(lines)


def _format_results_markdown(result) -> str:
    """Render the results panel as markdown with stat cards and summary."""
    blank_label = "Yes" if result.is_blank else "No"
    blank_count = 1 if result.is_blank else 0

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
    <div class="biodex-stat-value">{blank_count}</div>
    <div class="biodex-stat-label">Blank (0 or 1)</div>
  </div>
  <div class="biodex-stat">
    <div class="biodex-stat-value">{result.person_count}</div>
    <div class="biodex-stat-label">Humans</div>
  </div>
  <div class="biodex-stat">
    <div class="biodex-stat-value">{result.vehicle_count}</div>
    <div class="biodex-stat-label">Vehicles</div>
  </div>
</div>

**Blank / no-animal image?** {blank_label}

### Top detections

{_format_top_detections(result.detections)}

### Summary

{result.summary}
"""


def analyze_image(
    image: Image.Image | None,
    threshold: float,
):
    """
    Main analysis handler: detect, annotate, and prepare exports.

    Returns tuple for Gradio outputs:
    original, annotated, results markdown, annotated file, csv file.
    """
    if image is None:
        raise gr.Error("Please upload a camera trap image (JPG or PNG) first.")

    try:
        if not isinstance(image, Image.Image):
            image = Image.open(image)

        result = run_detection(image, threshold=threshold)
        annotated = draw_detections(image, result.detections)
        results_md = _format_results_markdown(result)

        annotated_path = save_annotated_image(annotated)
        csv_path = detections_to_csv(
            result.detections,
            image_name="upload",
            threshold=threshold,
        )

        return (
            image,
            annotated,
            results_md,
            gr.update(value=annotated_path, visible=True),
            gr.update(value=csv_path, visible=True),
        )

    except gr.Error:
        raise
    except Exception as exc:
        tb = traceback.format_exc()
        raise gr.Error(
            f"Analysis failed: {exc}\n\n"
            "If this is your first run, MegaDetector may still be downloading model weights. "
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
            """
            <div class="biodex-header">
                <h1>BioDex — Local AI for Wildlife Camera Traps</h1>
                <p class="biodex-tagline">
                    Detect animals, filter blanks, and export results — 100% on your machine.
                </p>
            </div>
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                input_image = gr.Image(
                    label="Upload camera trap image",
                    type="pil",
                    sources=["upload"],
                    height=360,
                )
                threshold = gr.Slider(
                    minimum=0.05,
                    maximum=0.95,
                    value=0.25,
                    step=0.05,
                    label="Confidence threshold",
                    info="Higher = fewer, more confident detections",
                )
                analyze_btn = gr.Button("Analyze Image", variant="primary", size="lg")

        with gr.Row():
            with gr.Column():
                original_out = gr.Image(
                    label="Original",
                    type="pil",
                    interactive=False,
                    height=400,
                )
            with gr.Column():
                annotated_out = gr.Image(
                    label="Annotated detections",
                    type="pil",
                    interactive=False,
                    height=400,
                )

        results_panel = gr.Markdown(label="Results")

        gr.Markdown("### Export results")
        with gr.Row():
            download_image = gr.File(
                label="Download annotated image (PNG)",
                visible=False,
            )
            download_csv = gr.File(
                label="Download detections (CSV)",
                visible=False,
            )

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
            inputs=[input_image, threshold],
            outputs=[
                original_out,
                annotated_out,
                results_panel,
                download_image,
                download_csv,
            ],
            show_progress="full",
        )

    return demo


if __name__ == "__main__":
    app = build_app()
    app.launch(theme=APP_THEME, css=CUSTOM_CSS)
