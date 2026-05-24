# BioDex

**Local AI for wildlife camera trap analysis and biodiversity monitoring.**

BioDex is a privacy-first desktop tool that helps researchers, citizen scientists, and land managers triage camera trap images — detect animals, filter blanks, classify species, draw bounding boxes, and export results. Everything runs on your machine. No cloud API calls during analysis.

---

## What's new in v0.2

- **Optional species classification** — SpeciesNet runs locally on animal crops (toggle in UI)
- **Professional visualization** — color-coded boxes, confidence labels, overlap-aware placement
- **Rich exports** — CSV with species fields + structured JSON export
- **Polished Gradio UI** — stat cards, detections table, prominent export buttons
- **Typed pipeline** — structured `AnalysisResult` objects across the `core/` modules

---

## Why BioDex exists

Camera traps generate *millions* of images. Most are empty — wind-blown branches, passing shadows, or nothing at all. Reviewing them manually is slow and expensive. BioDex uses [MegaDetector v5a](https://github.com/agentmorris/MegaDetector) to find animals, people, and vehicles, and optionally [SpeciesNet](https://github.com/google/cameratrapai) to suggest species — so you can focus on the images that matter.

BioDex is built for **defensive, protective use of AI**: biodiversity monitoring, habitat assessment, and conservation research — not surveillance or military applications.

---

## Quick start

**Requirements:** Python 3.10–3.12, ~3 GB disk space (including model weights after first run).

```powershell
# Clone or download this repo, then:
cd BioDex

python -m venv .venv
.\.venv\Scripts\activate          # Windows
# source .venv/bin/activate         # macOS / Linux

pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:7860** in your browser, upload a JPG or PNG camera trap image, and click **Analyze Image**.

> **First run:** MegaDetector downloads model weights (~280 MB) once. If you enable species classification, SpeciesNet downloads additional weights (~100 MB). Internet is required for first-time downloads; all later analysis works offline.

### Optional: GPU acceleration

If you have an NVIDIA GPU, install the CUDA build of PyTorch for faster inference:

```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

CPU-only mode works fine for occasional single-image analysis.

---

## Features

### Current (v0.2)

- Upload JPG/PNG camera trap images
- MegaDetector v5a detection (animal, person, vehicle)
- Optional SpeciesNet species classification on animal crops
- Adjustable confidence threshold (default 0.25)
- Side-by-side original vs. annotated view
- Stat cards: totals, animals, people, vehicles, blank status
- Detections table with species and bbox columns
- Export annotated PNG, detections CSV, and results JSON
- 100% local inference — your images never leave your computer

### Planned

See [docs/roadmap.md](docs/roadmap.md) for batch processing, video support, geofencing, and more.

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
├── requirements.txt
├── core/               # Not named utils — avoids YOLOv5 import conflict
│   ├── types.py        # AnalysisResult, DetectionRecord
│   ├── detector.py     # MegaDetector pipeline
│   ├── classifier.py   # SpeciesNet wrapper
│   ├── visualization.py
│   └── exports.py
├── examples/           # Place sample images here for testing
└── docs/
    └── roadmap.md
```

---

## How it works

1. You upload a camera trap image.
2. MegaDetector v5a runs locally and returns bounding boxes for animals, people, and vehicles.
3. Detections below your confidence threshold are filtered out.
4. If species classification is enabled, BioDex crops each animal detection and runs SpeciesNet locally.
5. If nothing passes the threshold, the image is flagged as a likely **blank**.
6. BioDex draws annotated boxes and lets you download PNG, CSV, and JSON results.

**SpeciesNet note:** The classifier covers ~2,000 taxa from diverse regions, but accuracy varies by geography and camera setup. Treat species labels as suggestions for expert review, not ground truth.

---

## Roadmap

| Version | Focus |
|---------|-------|
| **v0.2** (now) | Species classification, improved viz, JSON export |
| **v0.3+** | Batch processing, video clips, geofencing UI |

Full details: [docs/roadmap.md](docs/roadmap.md)

---

## Contributing

Contributions are welcome! This project is intentionally small and readable — a good place to start if you care about conservation tech.

1. Fork the repo
2. Create a feature branch
3. Make your changes with clear commits
4. Open a pull request

Ideas for contributions: batch mode, Wildlife Insights export, geofencing UI, documentation improvements.

---

## Conservation framing

BioDex exists to help people **protect biodiversity**, not to enable surveillance or harm. We encourage use by:

- Field biologists and ecologists
- Land trusts and protected area managers
- Citizen science programs
- Students learning conservation technology

Please use BioDex responsibly and in accordance with local laws and ethical guidelines for wildlife monitoring.

---

## License

BioDex is released under the [MIT License](LICENSE).

MegaDetector and SpeciesNet are developed by the conservation AI community and are subject to their own licenses. See their respective repositories for details and citation information.

---

## Acknowledgments

- [MegaDetector](https://github.com/agentmorris/MegaDetector) — detection model
- [SpeciesNet](https://github.com/google/cameratrapai) — species classification
- [LILA BC](https://lila.science/) — camera trap datasets and community
- Everyone working to make conservation AI accessible and open

---

## Screenshot

_Screenshot placeholder — run `python app.py` and upload a camera trap image to see BioDex in action._

Sample test image from MegaDetector docs:
https://github.com/agentmorris/MegaDetector/raw/main/images/orinoquia-thumb-web.jpg
