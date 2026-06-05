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

## Quick start

**Requirements:** Python 3.10–3.12, ~3 GB disk space (including model weights after first run).

```powershell
pip install -r requirements.txt
python scripts/fetch_examples.py   # optional but recommended for demo
python app.py
```

> **First run:** MegaDetector downloads model weights (~280 MB) once. SpeciesNet downloads additional weights (~214 MB) when first enabled. Internet is required for first-time downloads; all later analysis works offline.

### Optional: GPU acceleration (RunPod / NVIDIA H100)

Default `pip install torch` may install a CUDA build incompatible with your driver (inference falls back to CPU). On RunPod H100-class pods:

```bash
bash scripts/install_biodex.sh    # ordered install (protobuf + megadetector first)
source .venv/bin/activate
bash scripts/setup_gpu.sh         # cu124 torch — use the H100
python scripts/test_mega_load.py  # should print GPU available: True, device cuda:0
python scripts/smoke_test.py --species
```

One-shot on a fresh pod: `bash scripts/runpod_setup.sh`

### Batch demo (LinkedIn)

Multi-image aggregate stats + master CSV/JSON/annotated ZIP — screenshot-ready output:

```bash
git clone https://github.com/FratresMedAI/BioDex.git && cd BioDex
bash scripts/runpod_setup.sh          # or install_biodex.sh + setup_gpu.sh
source .venv/bin/activate
python scripts/fetch_examples.py      # 6 MegaDetector demo JPGs
python scripts/batch_smoke.py --species
```

Expected after first GPU run (H100, threshold 0.25): **7 animals across 6 images** — e.g. Ocelot, Island Fox, Puma, Plains Zebra, Silver Pheasant, Bird×2 — with paths under `/tmp/biodex-batch-demo/` (`batch_summary.csv`, `batch_summary.json`, `batch_annotated.zip`).

For the Gradio UI: expose port **7860**, open **Batch Folder**, upload `examples/*.jpg`.

Full screenshot checklist: [docs/demo.md](docs/demo.md)

### Fresh environment (venv or conda)

**Recommended (avoids protobuf ResolutionImpossible):**

```bash
git clone https://github.com/FratresMedAI/BioDex.git && cd BioDex
bash scripts/install_biodex.sh
source .venv/bin/activate
python scripts/fetch_examples.py
```

Do **not** rely on plain `pip install -r requirements.txt` alone — see `constraints.txt` and `scripts/install_biodex.sh`.

### Development and testing
pytest tests/ -v -m "not slow"
python -m mypy core
python -m ruff check core tests app.py
python scripts/smoke_test.py
python scripts/smoke_test.py --species
python scripts/batch_analyze.py examples/ -o /tmp/biodex-out --recursive
```

Install editable with CLI extras: `pip install -e ".[dev,cli]"`

Manual lint (no pre-commit hook yet): `ruff check .` and `mypy core`

### Fresh environment (venv or conda)

**venv (recommended):**

```powershell
python -m venv .venv
.\.venv\Scripts\activate   # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
# Optional protobuf pin for megadetector-first installs:
pip install -r requirements.txt -c constraints.txt
python scripts/fetch_examples.py
```

**conda:**

```bash
conda create -n biodex python=3.11 -y
conda activate biodex
pip install -r requirements.txt
```

### Troubleshooting

**Sample image missing:** Run `python scripts/fetch_examples.py`

**SpeciesNet / MegaDetector protobuf warning:** See [Reproducing protobuf conflict](#reproducing-protobuf-conflict) below. Try a fresh virtual environment if pip reports conflicts.

**Wrong megadetector package:** Ensure `megadetector>=10.0,<11.0` — version 5.x on PyPI is unrelated and breaks imports.

**Species labels look wrong:** SpeciesNet accuracy varies by region. Treat species output as a suggestion for expert review.

---

## Known limitations

- No historical `pyproject.toml`-only install path before v0.4 packaging pass; use `requirements.txt` or `pip install -e .` after pulling latest.
- Loose dependency resolution can still surface **protobuf conflicts** between MegaDetector (via ultralytics-yolov5, `protobuf<=3.20.1`) and SpeciesNet/onnx (prefer newer protobuf).
- Test coverage is unit-focused; edge cases for corrupt images, zero detections, classification failures, and non-RGB inputs are in `tests/` but full model inference is marked `@pytest.mark.slow`.
- Gradio UI progress and error display improved in v0.4 but browser batch uploads remain limited for very large folders — prefer `scripts/batch_analyze.py` or `biodex analyze` CLI.
- Configuration is environment-driven (`BIODEX_*` vars); no YAML file yet.
- `examples/` may be empty until `scripts/fetch_examples.py` is run; smoke test falls back with a clear message.
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
