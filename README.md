# BioDex

![CI](https://github.com/FratresMedAI/BioDex/actions/workflows/ci.yml/badge.svg)

**Local, privacy-first AI for wildlife camera trap analysis.**

BioDex helps researchers, citizen scientists, and land managers triage camera trap images on their own machine — detect animals, filter blanks, identify species, annotate photos for reports, and export structured results. No cloud API calls during analysis.

---

## What's new in v0.4

- **Report-grade visualization** — stroked labels, RGBA overlays, corner brackets for tiny detections, optional legend
- **Smarter species presentation** — confidence tiers (high / borderline / uncertain), blank-taxa filtering, expanded crops
- **Demo Mode tab** — one-click Run Demo with bundled ocelot sample + species classification
- **Polished UI** — shared settings panel, welcome guide, status feedback, cohesive Single + Batch tabs
- **Reliable samples** — `scripts/fetch_examples.py` downloads a known-good ocelot demo image

---

## Try the demo in 30 seconds

```powershell
cd BioDex
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python scripts/fetch_examples.py
python app.py
```

Open **http://127.0.0.1:7860**, open the **Demo Mode** tab, and click **Run Demo**.

Expected result on the bundled sample: **1 animal**, species **Ocelot** at high confidence, with a clean annotated image ready to export.

Full demo script: [docs/demo.md](docs/demo.md)

---

## Why BioDex exists

Camera traps generate *millions* of images. Most are empty — wind-blown branches, passing shadows, or nothing at all. Reviewing them manually is slow and expensive. BioDex uses [MegaDetector v5a](https://github.com/agentmorris/MegaDetector) to find animals, people, and vehicles, and optionally [SpeciesNet](https://github.com/google/cameratrapai) to suggest species — so you can focus on the images that matter.

BioDex is built for **defensive, protective use of AI**: biodiversity monitoring, habitat assessment, and conservation research — not surveillance or military applications.

---

## Install

**Requirements:** Python 3.10–3.12, ~3 GB disk for model weights after first run.

```bash
git clone https://github.com/FratresMedAI/BioDex.git && cd BioDex
bash scripts/install_biodex.sh          # protobuf-safe megadetector + speciesnet + editable install
source .venv/bin/activate
bash scripts/setup_gpu.sh               # optional: CUDA torch on RunPod / NVIDIA GPUs
```

Manual install:

```bash
python -m venv .venv && source .venv/bin/activate
pip install "protobuf==3.20.1"
pip install "megadetector>=10.0,<11.0" "speciesnet>=5.0,<6.0" "torch>=2.0"
pip install -e ".[ui,dev]"
```

> **First run:** MegaDetector (~280 MB) and SpeciesNet (~214 MB) download once when first used. Analysis is offline afterward.

---

## Headless batch CLI (primary workflow)

Process a folder of camera-trap images and write master CSV/JSON, per-image artifacts, annotated ZIP, and a text report:

```bash
# 1. Download realistic multi-animal data (Channel Islands / LILA, ~72 frames)
python -m scripts.demo_batch --prepare-only

# 2. Run the product CLI
biodex batch ~/.cache/biodex/channel-islands-demo \
  --output /tmp/biodex-batch-out \
  --classify-species \
  --recursive

cat /tmp/biodex-batch-out/batch_report.txt
ls -lh /tmp/biodex-batch-out/
```

**Verified output (H100, threshold 0.25):**

```
Images processed: 72
Blanks: 15 (20.8%) | Failed: 0
Animals: 237 | People: 0 | Vehicles: 0
Images with 2+ animals: 47
Top species: Rodent (69), Bird (47), Island Fox (12), …
```

Per-image peaks include **11–12 animals** in dense timelapse-style frames. Artifacts: `batch_report.txt` (1.4K), `batch_summary.csv` (56K), `batch_summary.json` (283K), `batch_annotated.zip` (~170M), `images/` (72 subfolders).

> **Note:** `examples/` holds 6 UI demo thumbs only. Realistic batch data lives in `~/.cache/biodex/channel-islands-demo/` after `--prepare-only`.

**Outputs in `--output`:**

| File | Description |
|------|-------------|
| `batch_report.txt` | Aggregate summary (images, animals, blanks, species, failures) |
| `batch_summary.csv` | Master detections table |
| `batch_summary.json` | Structured batch payload |
| `batch_annotated.zip` | Annotated PNGs (up to 100 by default) |
| `images/` | Per-image annotated PNG, CSV, and JSON |

**Exit codes:** `0` success · `1` fatal (no images) · `2` partial failures (summary still written)

**Options:** `--threshold 0.25` · `--no-recursive` · `--verbose` · `--zip-limit 100`

Your own field data:

```bash
biodex batch /path/to/camera_trap_folder -o ./results --classify-species --recursive
```

---

## Interactive UI (optional)

```bash
biodex-ui
# or: python app.py
```

Open **http://127.0.0.1:7860** — Demo Mode tab for single-image demo; **Batch Folder** tab for interactive uploads.

```bash
python scripts/fetch_examples.py   # 6 MegaDetector demo thumbs for Try Demo
```

---

## Quick smoke test

```bash
python scripts/smoke_test.py --species   # install health check: 1 ocelot image only
python -m scripts.demo_batch --prepare-only && biodex batch ~/.cache/biodex/channel-islands-demo -o /tmp/out --classify-species
```

`smoke_test.py` confirms models load; **`biodex batch`** is the real volume workflow.

### GPU on RunPod / H100

```bash
bash scripts/setup_gpu.sh
python scripts/test_mega_load.py   # expect cuda:0
biodex batch ~/.cache/biodex/channel-islands-demo -o /tmp/out --classify-species
```

One-shot setup: `bash scripts/runpod_setup.sh`

---

## Development

```bash
pytest tests/ -v -m "not slow"
ruff check .
mypy . --strict
pip install -e ".[ui,dev]"
```

Legacy wrapper (same as `biodex batch`): `python scripts/batch_analyze.py examples/ -o /tmp/out -r --classify-species`

### Troubleshooting

**Sample image missing:** Run `python scripts/fetch_examples.py` (UI thumbs only).

**No batch data / empty folder:** Run `python -m scripts.demo_batch --prepare-only` first.

**`biodex: command not found`:** Run `pip install -e ".[ui,dev]"` from the repo root.

**Exit code 1:** No images in input folder, or folder path wrong. Check `--recursive` if images are in subfolders.

**Exit code 2:** Some images failed; see `batch_report.txt` failures section — summary artifacts are still written.

**SpeciesNet / MegaDetector protobuf warning:** Use `bash scripts/install_biodex.sh` (pins `protobuf==3.20.1` before megadetector).

**Wrong megadetector package:** Ensure `megadetector>=10.0,<11.0` — PyPI 5.x is unrelated.

**GPU falls back to CPU:** Run `bash scripts/setup_gpu.sh` on RunPod/NVIDIA pods.

**Species labels look wrong:** SpeciesNet accuracy varies by region — treat as triage suggestions for expert review.

---

## Known limitations

- No historical `pyproject.toml`-only install path before v0.4 packaging pass; use `requirements.txt` or `pip install -e .` after pulling latest.
- Loose dependency resolution can still surface **protobuf conflicts** between MegaDetector (via ultralytics-yolov5, `protobuf<=3.20.1`) and SpeciesNet/onnx (prefer newer protobuf).
- Test coverage is unit-focused; edge cases for corrupt images, zero detections, classification failures, and non-RGB inputs are in `tests/` but full model inference is marked `@pytest.mark.slow`.
- Gradio UI is best for interactive review; for folders of 100+ images use **`biodex batch`** (headless CLI).
- Configuration is environment-driven (`BIODEX_*` vars); no YAML file yet.
- `examples/` holds 6 UI demo thumbs; realistic batch data is in `~/.cache/biodex/channel-islands-demo/` after `demo_batch --prepare-only`.
- Strict mypy/ruff enforcement applies to `core/` in CI; UI scripts are lint-checked but not fully typed.

---

## Verification

After install, run these commands from the repository root:

```powershell
pip install -r requirements-ci.txt
pytest tests/ -v -m "not slow"
python -m mypy core
python -m ruff check core tests app.py
python scripts/fetch_examples.py
python scripts/smoke_test.py
python -c "from app import build_app; build_app(); print('app ok')"
```

With full runtime dependencies:

```powershell
pip install -r requirements.txt
python scripts/smoke_test.py --species
python scripts/batch_analyze.py examples/ -o ./batch_out
```

---

## Reproducing protobuf conflict

MegaDetector 10.x pulls `protobuf<=3.20.1` through its YOLOv5 stack. SpeciesNet and onnx often want **protobuf ≥ 4.25**. Pip may install a version that satisfies only one side.

**Mitigation steps:**

1. Create a **fresh venv** (or conda env) — do not reuse an env where unrelated packages pinned protobuf.
2. Install BioDex deps: `pip install -r requirements.txt`
3. Optional stricter pin attempt: `pip install -c constraints.txt -r requirements.txt`
4. Verify detection only: `python scripts/smoke_test.py`
5. Verify species path: `python scripts/smoke_test.py --species`
6. If SpeciesNet fails at import or runtime, capture `pip show protobuf megadetector speciesnet` and open an issue — full resolution may require upstream alignment.

---

## Features (v0.4)

- **Single-image analysis** with side-by-side original vs annotated view
- **Batch folder triage** — multi-file upload, summary table, master CSV/JSON
- **MegaDetector v5a** — animal, person, vehicle detection with adjustable threshold
- **SpeciesNet species ID** — optional local classification with confidence tiers and alternatives
- **Report-ready annotations** — color-coded boxes, legend, overlap-aware labels
- **Exports** — PNG, CSV, JSON, and ZIP bundle (single image); batch CSV/JSON/ZIP
- **100% local** — your images never leave your computer

See [docs/roadmap.md](docs/roadmap.md) for upcoming video support, geofencing, and pipeline exports.

---

## Tech stack

| Component | Technology |
|-----------|------------|
| UI | [Gradio 5+](https://gradio.app/) |
| Detection | [MegaDetector v5a](https://pypi.org/project/megadetector/) (MDV5A) |
| Species ID | [SpeciesNet](https://pypi.org/project/speciesnet/) (optional) |
| Deep learning | PyTorch |
| Image processing | Pillow |
| Data export | pandas (CSV), stdlib json |
| Language | Python 3.10–3.12 |

---

## Project structure

```
BioDex/
├── app.py              # Gradio UI entry point
├── ui/                 # Styles and HTML components
├── core/               # Detection, species, viz, exports, batch, cli (see docs/adr-core-package.md)
├── examples/           # Sample manifest + demo images
├── scripts/            # fetch_examples.py, smoke_test.py, batch_analyze.py
└── docs/               # roadmap, demo guide, screenshots
```

---

## Screenshots and demo

See [docs/demo.md](docs/demo.md) for a step-by-step demo script and screenshot tips.

Save captures to `docs/screenshots/` for README and presentations.

---

## Roadmap

| Version | Focus |
|---------|-------|
| **v0.4** (now) | Demo-ready polish, viz quality, species tiers, Try Demo |
| **v0.5+** | Geofencing UI, video clips, Wildlife Insights export |

Full details: [docs/roadmap.md](docs/roadmap.md)

---

## Contributing

Contributions are welcome! This project is intentionally small and readable.

Ideas: geofencing UI, video support, Wildlife Insights export, documentation improvements.

---

## Conservation framing

BioDex exists to help people **protect biodiversity**, not to enable surveillance or harm.

Please use BioDex responsibly and in accordance with local laws and ethical guidelines for wildlife monitoring.

---

## License

BioDex is released under the [MIT License](LICENSE).

MegaDetector and SpeciesNet are subject to their own licenses — see their repositories for citation information.

---

## Acknowledgments

- [MegaDetector](https://github.com/agentmorris/MegaDetector)
- [SpeciesNet](https://github.com/google/cameratrapai)
- [LILA BC](https://lila.science/)
