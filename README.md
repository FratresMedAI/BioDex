<p align="center">
  <img src="https://raw.githubusercontent.com/Fratres-X-Natura/BioDex/main/docs/images/hero.png" alt="BioDex Field Review — local AI for wildlife camera traps" width="920">
</p>

<h1 align="center">BioDex</h1>

<p align="center">
  <strong>Local, privacy-first AI for wildlife camera-trap analysis.</strong><br>
  Detect animals · filter blanks · identify species · export field-ready results — on your machine, not in the cloud.
</p>

<p align="center">
  <sub><strong>Note:</strong> This repository lives under the <a href="https://github.com/Fratres-X-Natura">Fratres-X-Natura</a> account as the dedicated home for wildlife and defensive monitoring tooling.</sub>
</p>

<p align="center">
  <a href="https://pypi.org/project/biodex/"><img src="https://img.shields.io/pypi/v/biodex.svg" alt="PyPI"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10--3.12-blue.svg" alt="Python 3.10–3.12"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License"></a>
  <a href="CHANGELOG.md"><img src="https://img.shields.io/badge/version-1.0.3-brightgreen.svg" alt="v1.0.3"></a>
  <a href="https://github.com/Fratres-X-Natura/BioDex/actions/workflows/ci.yml"><img src="https://github.com/Fratres-X-Natura/BioDex/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
</p>

<p align="center">
  <a href="#quick-start--install-and-run"><strong>Install &amp; run</strong></a> ·
  <a href="#why-biodex">Why BioDex</a> ·
  <a href="#optional-ai-review-byok">AI review</a> ·
  <a href="#batch-cli">CLI</a> ·
  <a href="#developers">Developers</a>
</p>

---

## Quick start — install and run

**This is how you use BioDex.** Install from [PyPI](https://pypi.org/project/biodex/), then launch the field-review UI.

| | |
|---|---|
| **Python** | 3.10, 3.11, or 3.12 |
| **Platforms** | macOS · Linux · Windows |
| **First run** | Downloads model weights once (~500 MB), then runs offline |
| **Browser** | **http://127.0.0.1:7860** (auto-fallback 7860–7879) |

**Mac / Linux / Windows** — run in order:

```bash
pip install biodex
pip install "biodex[ui,video]" --prefer-binary
pip install protobuf==3.20.1
pip install "biodex[heavy]" --prefer-binary
biodex-ui
```

Open the URL printed in your terminal. Use **Batch** to process a folder, or **Quick demo** for an instant preview.

<details>
<summary><strong>One-liner (copy-paste)</strong></summary>

```bash
pip install biodex && pip install "biodex[ui,video]" --prefer-binary && pip install protobuf==3.20.1 && pip install "biodex[heavy]" --prefer-binary && biodex-ui
```

</details>

| Tip | Detail |
|-----|--------|
| **Windows** | Always pass `--prefer-binary` on the heavy step to avoid slow or failed source builds (`cmake`, `onnx`). |
| **Do not use** | `pip install "biodex[all]"` — it does **not** include MegaDetector/SpeciesNet. Use the commands above. |
| **Privacy** | Images never leave your machine during detection. Optional LLM review is bring-your-own-key only. |

---

## Why BioDex

Camera traps generate millions of frames. Most pipelines are cloud-only, expensive per image, or awkward for sensitive field data. BioDex is built for teams who need **reproducible, offline-first** triage on their own hardware.

| Capability | What you get |
|------------|--------------|
| **Detection** | MegaDetector v5a — animal, person, vehicle, blank filtering |
| **Species ID** | SpeciesNet classification with confidence scores |
| **Batch review** | Annotated frames, tables, exports, optional per-frame LLM notes |
| **Video** | Frame sampling and timeline export (`[video]` extra) |
| **Exports** | Wildlife Insights, iNaturalist drafts, SQLite, timelapse JSON, EcoSentinel hook |
| **CLI** | Headless `biodex batch` for large folders without a browser |

Built for conservation research, field review, and defensive wildlife monitoring.

---

## Optional AI review (BYOK)

Core detection runs **fully offline**. AI review is an optional power feature — your API key, your provider, your choice of model.

1. Open **Use via API** in the footer.
2. Choose a provider, paste your API key, pick a model (or type a custom model ID), then **Save**.
3. After a batch run, select a frame and click **AI review (LLM)** for a field note: scene summary, species second opinion, and data-quality flags.

**Privacy:** Keys are stored locally in `~/.cache/biodex/settings.json` and sent only to the provider you choose — never to BioDex servers. See [SECURITY.md](SECURITY.md).

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
| `all` | ui + video + analytics + dev + desktop + edge | **No inference stack** — not a substitute for quick start |

---

## Installation troubleshooting

<details>
<summary><strong>Clean install</strong> (upgrading from 0.5.0 or fixing a broken env)</summary>

```bash
pip uninstall biodex megadetector speciesnet onnx onnx2torch -y
pip cache purge
pip install biodex
pip install "biodex[ui,video]" --prefer-binary
pip install protobuf==3.20.1
pip install "biodex[heavy]" --prefer-binary
biodex-ui
```

On Windows, prefer a fresh virtual environment:

```bat
python -m venv .venv
.venv\Scripts\activate
```

Then run the **Quick start** commands again.

</details>

<details>
<summary><strong><code>cmake</code> / <code>onnx</code> build errors on Windows</strong></summary>

1. Use `--prefer-binary` on every BioDex extra install.
2. Pin protobuf first: `pip install protobuf==3.20.1`
3. Install `[heavy]` in a **separate** command after `[ui,video]`.
4. If it still fails, create a fresh venv and repeat quick start from scratch.

</details>

<details>
<summary><strong>Slow dependency resolution</strong></summary>

Avoid `biodex[all,heavy]` in one command on Windows. Install in the four-step order from **Quick start**.

</details>

---

## Batch CLI

For large folders (100+ images), no browser:

```bash
biodex batch /path/to/images -o ./results --classify-species --recursive
biodex batch /path/to/images -o ./results --chunk-size 500 --torch-compile
biodex video /path/to/clip.mp4 -o ./video-results --fps 1 --max-frames 120
```

Environment variables: `BIODEX_DETECTOR_MODEL`, `BIODEX_TORCH_COMPILE`, `BIODEX_GEOFENCE_REGION`, `BIODEX_AUDIT_LOG=1`

## Docker

```bash
docker build -t biodex:cpu -f Dockerfile .
docker run --rm -p 7860:7860 biodex:cpu
```

GPU image: `docker build -t biodex:gpu -f Dockerfile.gpu .`

---

## Developers

Clone the repository:

```bash
git clone https://github.com/Fratres-X-Natura/BioDex.git
cd BioDex
```

Install in editable mode with development dependencies:

```bash
pip install -e ".[ui,heavy,dev]" --prefer-binary
pre-commit install
```

Run tests and linting:

```bash
pytest tests/ -v -m "not slow"
ruff check .
mypy core ui
```

For full contribution guidelines see [CONTRIBUTING.md](CONTRIBUTING.md).

[CHANGELOG.md](CHANGELOG.md) · [docs/roadmap.md](docs/roadmap.md) · [SECURITY.md](SECURITY.md)

---

<p align="center">
  <sub>MIT License · Powered by <a href="https://github.com/agentmorris/MegaDetector">MegaDetector</a> and <a href="https://github.com/google/cameratrapai">SpeciesNet</a></sub>
</p>
