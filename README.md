# BioDex

**Local AI for wildlife camera trap analysis and biodiversity monitoring.**

BioDex is a simple, privacy-first desktop tool that helps researchers, citizen scientists, and land managers triage camera trap images — detect animals, filter blanks, draw bounding boxes, and export results. Everything runs on your machine. No cloud API calls during analysis.

---

## Why BioDex exists

Camera traps generate *millions* of images. Most are empty — wind-blown branches, passing shadows, or nothing at all. Reviewing them manually is slow and expensive. BioDex uses [MegaDetector v5a](https://github.com/agentmorris/MegaDetector), a proven conservation AI model, to automatically find animals, people, and vehicles so you can focus on the images that matter.

BioDex is built for **defensive, protective use of AI**: biodiversity monitoring, habitat assessment, and conservation research — not surveillance or military applications.

---

## Quick start

**Requirements:** Python 3.10–3.13, ~2 GB disk space (including model weights after first run).

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

> **First run:** MegaDetector downloads model weights (~200 MB) once. This requires internet; all later analysis works offline.

### Optional: GPU acceleration

If you have an NVIDIA GPU, install the CUDA build of PyTorch for faster inference:

```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

CPU-only mode works fine for occasional single-image analysis.

---

## Features

### Current (v1)

- Upload JPG/PNG camera trap images
- MegaDetector v5a detection (animal, person, vehicle)
- Adjustable confidence threshold (default 0.25)
- Side-by-side original vs. annotated view
- Detection stats: totals, animals, blanks, humans, vehicles
- Top detections list with confidence scores
- Export annotated PNG and detections CSV
- 100% local inference — your images never leave your computer

### Planned

See [docs/roadmap.md](docs/roadmap.md) for v0.2+ plans including species classification, batch processing, and video support.

---

## Tech stack

| Component | Technology |
|-----------|------------|
| UI | [Gradio 5](https://gradio.app/) |
| Detection | [MegaDetector v5a](https://pypi.org/project/megadetector/) (MDV5A) |
| Deep learning | PyTorch |
| Image processing | Pillow |
| Data export | pandas (CSV) |
| Language | Python 3.10+ |

---

## Project structure

```
BioDex/
├── app.py              # Gradio UI entry point
├── requirements.txt
├── core/               # Detection, visualization, export (not named utils — YOLOv5 conflict)
│   ├── detector.py     # MegaDetector inference
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
4. If nothing passes the threshold, the image is flagged as a likely **blank**.
5. BioDex draws boxes on the image and lets you download results.

MegaDetector finds *where* things are — it does **not** identify species. That is on the roadmap.

---

## Roadmap

| Version | Focus |
|---------|-------|
| **v1** (now) | Single-image detection, visualization, CSV/PNG export |
| **v0.2+** | Species classification, batch processing, video clips |

Full details: [docs/roadmap.md](docs/roadmap.md)

---

## Contributing

Contributions are welcome! This project is intentionally small and readable — a good place to start if you care about conservation tech.

1. Fork the repo
2. Create a feature branch
3. Make your changes with clear commits
4. Open a pull request

Ideas for contributions: batch mode, better UI themes, integration with Timelapse/Wildlife Insights formats, documentation improvements.

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

MegaDetector is developed by the conservation AI community and is subject to its own license. See the [MegaDetector repository](https://github.com/agentmorris/MegaDetector) for details and citation information.

---

## Acknowledgments

- [MegaDetector](https://github.com/agentmorris/MegaDetector) — the detection model that powers this tool
- [LILA BC](https://lila.science/) — camera trap datasets and community
- Everyone working to make conservation AI accessible and open

---

## Screenshot

_Screenshot placeholder — run `python app.py` and upload a camera trap image to see BioDex in action._

Sample test image from MegaDetector docs:
https://github.com/agentmorris/MegaDetector/raw/main/images/orinoquia-thumb-web.jpg
