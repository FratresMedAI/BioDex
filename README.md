# BioDex

**Local AI for wildlife camera traps.** Detect animals, filter blanks, identify species, export results — on your machine, not in the cloud.

[![Python 3.10–3.12](https://img.shields.io/badge/python-3.10--3.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.1-brightgreen.svg)](CHANGELOG.md)
[![CI](https://github.com/FratresMedAI/BioDex/actions/workflows/ci.yml/badge.svg)](https://github.com/FratresMedAI/BioDex/actions/workflows/ci.yml)
[![Release](https://github.com/FratresMedAI/BioDex/actions/workflows/release.yml/badge.svg)](https://github.com/FratresMedAI/BioDex/actions/workflows/release.yml)

Built for conservation research, field review, and defensive wildlife monitoring (Fratres / EcoSentinel integration hooks).

---

## Run locally (do this)

**Mac / Linux**

```bash
git clone https://github.com/FratresMedAI/BioDex.git
cd BioDex
./run_biodex.sh
```

**Windows**

```bat
git clone https://github.com/FratresMedAI/BioDex.git
cd BioDex
run_biodex.bat
```

Your browser opens **http://127.0.0.1:7860**. Use the **Batch** tab to process a folder, or **Quick demo** for a fast preview.

First analysis downloads models once (~500 MB). After that, everything stays offline on your computer.

---

## v1.0 highlights

- **Pluggable models** — registry architecture (`core/models/`) with MegaDetector + SpeciesNet adapters
- **Batch performance** — chunking, cancel, ETA progress, optional `torch.compile`
- **Video foundations** — frame sampling + timeline export (`biodex video`, requires `[video]` extra)
- **Advanced exports** — Wildlife Insights, iNaturalist drafts, timelapse JSON, SQLite, EcoSentinel hook
- **Tabbed UI** — Dashboard, Batch, Video, Analytics, Settings
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

## Extras install matrix

```bash
pip install -e ".[ui,models]"           # Web UI + inference (default)
pip install -e ".[video]"               # OpenCV video support
pip install -e ".[analytics]"           # Heatmaps + diversity metrics
pip install -e ".[edge]"                # ONNX stubs (future edge deploy)
pip install -e ".[all]"                 # Everything
```

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

## Developers

```bash
pip install -e ".[ui,models,dev]"
pytest tests/ -v -m "not slow"
ruff check core app.py ui
mypy core app.py ui
pre-commit install   # optional
```

See [CHANGELOG.md](CHANGELOG.md), [docs/roadmap.md](docs/roadmap.md), [CONTRIBUTING.md](CONTRIBUTING.md), and [SECURITY.md](SECURITY.md).

---

MIT License. Uses [MegaDetector](https://github.com/agentmorris/MegaDetector) and [SpeciesNet](https://github.com/google/cameratrapai).
