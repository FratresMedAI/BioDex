# BioDex

**Local AI for wildlife camera traps.** Detect animals, filter blanks, identify species, export results — on your machine, not in the cloud.

[![Python 3.10–3.12](https://img.shields.io/badge/python-3.10--3.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.1-brightgreen.svg)](CHANGELOG.md)
[![CI](https://github.com/FratresMedAI/BioDex/actions/workflows/ci.yml/badge.svg)](https://github.com/FratresMedAI/BioDex/actions/workflows/ci.yml)
[![Release](https://github.com/FratresMedAI/BioDex/actions/workflows/release.yml/badge.svg)](https://github.com/FratresMedAI/BioDex/actions/workflows/release.yml)

---

## Quick start — install and run

**This is how you use BioDex.** Install from [PyPI](https://pypi.org/project/biodex/), then launch the web UI.

**Requirements:** Python **3.10**, **3.11**, or **3.12** · internet on first run (models download once, ~500 MB)

**Mac / Linux / Windows** — run these commands in order:

```bash
pip install biodex
pip install "biodex[ui,video]" --prefer-binary
pip install protobuf==3.20.1
pip install "biodex[heavy]" --prefer-binary
biodex-ui
```

Open **http://127.0.0.1:7860** in your browser. Use the **Batch** tab to process a folder, or **Quick demo** for a fast preview.

**Copy-paste one-liner:**

```bash
pip install biodex && pip install "biodex[ui,video]" --prefer-binary && pip install protobuf==3.20.1 && pip install "biodex[heavy]" --prefer-binary && biodex-ui
```

| Tip | Detail |
|-----|--------|
| **Windows** | Always pass `--prefer-binary` on the heavy step to avoid slow or failed source builds (`cmake`, `onnx` compile errors). |
| **Port in use** | The app tries **7860–7879** automatically if 7860 is busy. |
| **Do not use** | `pip install "biodex[all]"` — it does **not** include MegaDetector/SpeciesNet. Use the commands above. |
| **After first run** | Detection runs fully offline on your machine. |

Built for conservation research, field review, and defensive wildlife monitoring (Fratres / EcoSentinel integration hooks).

---

## v1.0 highlights

- **Pluggable models** — registry architecture (`core/models/`) with MegaDetector + SpeciesNet adapters
- **Batch performance** — chunking, cancel, ETA progress, optional `torch.compile`
- **Video foundations** — frame sampling + timeline export (`biodex video`, requires `[video]` extra)
- **Advanced exports** — Wildlife Insights, iNaturalist drafts, timelapse JSON, SQLite, EcoSentinel hook
- **Tabbed UI** — Dashboard, Batch, Video, Settings
- **Optional AI review (BYOK)** — per-frame LLM notes after batch runs (see below)
- **Docker** — CPU and GPU images for deployment
- **Release maturity** — stable API surface, strict typing/linting, and CI-gated quality

---

## Optional AI review (BYOK)

Core detection runs **fully offline** on your machine. AI review is an **optional** power feature:

1. Open **Use via API** in the footer.
2. Choose a provider, paste your API key, pick a model (or type a custom model ID), then **Save**.
3. After a batch run, select a frame and click **AI review (LLM)** for a field note: scene summary, species second opinion, and data-quality flags.

**Privacy:** API keys are stored locally in `~/.cache/biodex/settings.json` and sent only to the provider you choose — never to BioDex servers. See [SECURITY.md](SECURITY.md).

**Scope in v1.0.1:** batch frame review only. Single-image spot check, video key frames, and batch-level summaries are planned for v1.1. Not every model slug in the dropdown is guaranteed to work with every provider — use a custom model ID if needed.

---

## PyPI extras (reference)

| Extra | What it installs | When to use |
|-------|------------------|-------------|
| `ui` | Gradio web UI | **Required** — included in quick start |
| `video` | OpenCV (headless, wheel-pinned) | **Recommended** — Video tab / `biodex video` |
| `heavy` / `models` | MegaDetector, SpeciesNet, PyTorch, protobuf pin | **Required** — detection and species ID |
| `analytics` | matplotlib, seaborn | Library/API only (not used by the UI) |
| `edge` | onnxruntime stubs | Experimental edge deploy |
| `dev` | pytest, ruff, mypy | Contributors |
| `all` | ui + video + analytics + dev + desktop + edge | **No inference stack** — not a substitute for the quick start |

---

## Installation troubleshooting

### Clean install (upgrading from 0.5.0 or fixing a broken env)

```bash
pip uninstall biodex megadetector speciesnet onnx onnx2torch -y
pip cache purge
pip install biodex
pip install "biodex[ui,video]" --prefer-binary
pip install protobuf==3.20.1
pip install "biodex[heavy]" --prefer-binary
biodex-ui
```

On Windows, use a fresh virtual environment when possible:

```bat
python -m venv .venv
.venv\Scripts\activate
```

Then run the **Quick start** commands again.

### `cmake` / `onnx` build errors on Windows

SpeciesNet pulls `onnx` transitively. If pip tries to **build from source**:

1. Use `--prefer-binary` on every BioDex extra install.
2. Pin protobuf first: `pip install protobuf==3.20.1`
3. Install `[heavy]` in a **separate** command after `[ui,video]`.
4. If it still fails, create a fresh venv and repeat the quick start from scratch.

### Slow dependency resolution

Avoid `biodex[all,heavy]` in one command on Windows. Install in the four-step order from **Quick start**.

---

## Batch CLI

For large folders (100+ images), no browser:

```bash
biodex batch /path/to/images -o ./results --classify-species --recursive
biodex batch /path/to/images -o ./results --chunk-size 500 --torch-compile
biodex video /path/to/clip.mp4 -o ./video-results --fps 1 --max-frames 120
```

Environment variables: `BIODEX_DETECTOR_MODEL`, `BIODEX_TORCH_COMPILE`, `BIODEX_GEOFENCE_REGION`, `BIODEX_AUDIT_LOG=1`

## Docker quick start

```bash
docker build -t biodex:cpu -f Dockerfile .
docker run --rm -p 7860:7860 biodex:cpu
```

GPU:

```bash
docker build -t biodex:gpu -f Dockerfile.gpu .
```

---

## Developers (git clone)

End users should use **Quick start** (PyPI) above. Clone this repo only if you are contributing or hacking on BioDex locally.

```bash
git clone https://github.com/FratresMedAI/BioDex.git
cd BioDex
# Mac/Linux: ./run_biodex.sh
# Windows:    run_biodex.bat
```

Or manual setup:

```bash
pip install -e ".[ui,heavy,dev]" --prefer-binary
pre-commit install
pytest tests/ -v -m "not slow"
ruff check core app.py ui
mypy core app.py ui
```

See [CHANGELOG.md](CHANGELOG.md), [docs/roadmap.md](docs/roadmap.md), [CONTRIBUTING.md](CONTRIBUTING.md), and [SECURITY.md](SECURITY.md).

---

MIT License. Uses [MegaDetector](https://github.com/agentmorris/MegaDetector) and [SpeciesNet](https://github.com/google/cameratrapai).
