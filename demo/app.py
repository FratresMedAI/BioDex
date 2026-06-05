"""
BioDex — limited public Hugging Face demo.
Max 30 images · no ZIP · run locally for the full private app.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def _ensure_runtime_ml_deps() -> None:
    """Install onnx (prebuilt wheel) + speciesnet without protobuf conflicts."""
    packages = [
        ("onnx", "onnx==1.16.1"),
        ("speciesnet", "speciesnet>=5.0,<6.0"),
    ]
    for module, spec in packages:
        try:
            __import__(module)
        except ImportError:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", spec, "--no-deps", "-q"],
                check=False,
            )
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "protobuf==3.20.1", "--force-reinstall", "-q"],
        check=False,
    )


_ensure_runtime_ml_deps()

import gradio as gr
import pandas as pd
from core.batch import run_batch
from PIL import Image

GITHUB_REPO = "https://github.com/FratresMedAI/BioDex"
MAX_IMAGES = 30
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}

os.environ.setdefault("BIODEX_DEPLOY", "1")
os.environ.setdefault("BIODEX_HOST", "0.0.0.0")

BANNER = f"""
<div style="position:sticky;top:0;z-index:999;background:#991b1b;color:#fff;
padding:14px 18px;border:2px solid #fca5a5;border-radius:6px;margin-bottom:14px;
font-size:1rem;line-height:1.5;box-shadow:0 4px 12px rgba(0,0,0,.35);">
  <div style="font-size:1.1rem;font-weight:800;margin-bottom:6px;">
    LIMITED PUBLIC DEMO — NOT THE FULL APP
  </div>
  <div>Max {MAX_IMAGES} images · no ZIP export · shared servers (not private).</div>
  <a href="{GITHUB_REPO}" target="_blank" rel="noopener"
     style="color:#fde68a;font-weight:700;margin-top:8px;display:inline-block;">
    Get BioDex for real use — clone and run locally (free, private, unlimited)
  </a>
</div>
"""

EMPTY_DF = pd.DataFrame(columns=["File", "Animals", "Species", "Status"])


def _cap_paths(files: list[str] | None) -> tuple[list[str], str]:
    if not files:
        return [], ""
    paths = sorted(p for p in files if Path(p).suffix.lower() in IMAGE_SUFFIXES)
    if not paths:
        return [], ""
    if len(paths) <= MAX_IMAGES:
        return paths, ""
    note = f"Demo limit: showing first {MAX_IMAGES} of {len(paths)} images."
    return paths[:MAX_IMAGES], note


def process_folder(
    files: list[str] | None,
    threshold: float,
    classify_species: bool,
    progress: Any = gr.Progress(),  # noqa: B008
) -> tuple[str, pd.DataFrame, str, Any]:
    paths, note = _cap_paths(files)
    if not paths:
        raise gr.Error(f"Upload JPG/PNG images (max {MAX_IMAGES} for this demo).")

    images: list[tuple[str, Image.Image]] = []
    for path in paths:
        images.append((Path(path).name, Image.open(path).convert("RGB")))

    def on_progress(current: int, total: int, message: str) -> None:
        progress(current / total, desc=message)

    batch = run_batch(
        images,
        threshold=threshold,
        classify_species=classify_species,
        progress_callback=on_progress,
    )

    rows = []
    for result, (name, _) in zip(batch.results, images, strict=True):
        top_species = ""
        if result.species_counts:
            top_species = max(result.species_counts, key=result.species_counts.get)
        status = "error" if result.error else ("blank" if result.is_blank else "ok")
        rows.append(
            {
                "File": name,
                "Animals": result.animal_count,
                "Species": top_species,
                "Status": status,
            }
        )

    summary = (
        f"**{batch.total_images}** images · **{batch.animal_count}** animals · "
        f"**{batch.blank_count}** blanks"
    )
    if batch.failed:
        summary += f" · **{len(batch.failed)}** failed"
    if note:
        summary += f"\n\n_{note}_"

    progress(1.0, desc="Done")
    return summary, pd.DataFrame(rows), summary, gr.update(visible=False)


with gr.Blocks(title="BioDex Limited Demo") as demo:
    gr.HTML(BANNER)
    gr.Markdown("Upload a camera-trap folder, then **Process Folder**.")
    with gr.Row():
        uploads = gr.File(
            label="Camera-trap images",
            file_count="directory",
            file_types=["image"],
            type="filepath",
        )
        run_btn = gr.Button("Process Folder", variant="primary")
    with gr.Accordion("Settings", open=False):
        threshold = gr.Slider(0.05, 0.95, value=0.25, step=0.05, label="Threshold")
        species_on = gr.Checkbox(value=True, label="Species classification")
    stats = gr.Markdown("Ready.")
    table = gr.Dataframe(headers=["File", "Animals", "Species", "Status"], interactive=False)
    zip_btn = gr.DownloadButton("Annotated ZIP", visible=False, interactive=False)

    run_btn.click(
        process_folder,
        inputs=[uploads, threshold, species_on],
        outputs=[stats, table, stats, zip_btn],
        show_progress="full",
    )

demo.queue(default_concurrency_limit=2)
demo.launch(server_name="0.0.0.0", server_port=7860)
