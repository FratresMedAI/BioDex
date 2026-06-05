# BioDex Roadmap

An honest look at where BioDex is headed. Timelines are approximate — this is an open-source project built for conservation utility, not enterprise speed.

---

## v1 — Foundation (complete)

- [x] Single-image upload and analysis
- [x] MegaDetector v5a (MDV5A) local detection
- [x] Animal / person / vehicle bounding boxes
- [x] Blank image detection (no detections above threshold)
- [x] Confidence threshold slider
- [x] Annotated image + CSV export
- [x] Gradio web UI, fully local

---

## v0.2 — Species awareness (complete)

**Goal:** Move from "something is here" to "what species might this be?"

- [x] Integrate [SpeciesNet](https://github.com/google/cameratrapai) on MegaDetector animal crops
- [x] Top species suggestions with confidence scores (top-3 stored in exports)
- [x] Optional detection-only vs. detection + classification toggle
- [x] Professional PIL visualization with overlap-aware labels
- [x] JSON export for downstream tools

**Known limitation:** SpeciesNet is region-dependent; accuracy varies outside its training geography.

---

## v0.3 — Batch processing dashboard (complete)

**Goal:** Analyze folders, not just single images.

- [x] Multi-file upload for batch analysis (browser-safe, no server path exposure)
- [x] Progress bar and per-image results table
- [x] Summary statistics (blank count, detection totals, species frequency)
- [x] Bulk export of master CSV/JSON and annotated images ZIP (first 50)
- [x] Export bundle (ZIP) for single-image workflow
- [x] Visualization polish: adaptive fonts, category legend, label connectors
- [x] Species alternatives column in UI and exports

**Known limitation:** Very large folders (10k+ images) may be slow in the browser UI; use the batch CLI (`scripts/batch_analyze.py`, `biodex analyze`, or `python scripts/smoke_test.py --batch examples/`).

---

## v0.4.1 — Packaging and batch CLI (complete)

**Goal:** Package for install, harden core logging/tests, and support folder batch from the shell.

- [x] `pyproject.toml` with hatchling, ruff/mypy config, and `biodex` console script
- [x] `constraints.txt` and README protobuf mitigation
- [x] Audit metadata on `AnalysisResult` (`model_id`, `inference_ms`, `timestamp`)
- [x] Expanded pytest edge cases (`tests/test_detector.py`, strict `pytest.ini`)
- [x] Batch CLI: `scripts/batch_analyze.py` / `biodex analyze`
- [x] CI: pytest + ruff + mypy on `core/`

---

## v0.4 — Demo-ready polish (complete)

**Goal:** Make BioDex impressive and trustworthy for first-time users and conservation demos.

- [x] Report-grade visualization (stroked labels, RGBA overlays, corner brackets, legend toggle)
- [x] Species confidence tiers with borderline alternatives and Uncertain handling
- [x] Blank-taxa filtering and expanded animal crops for SpeciesNet
- [x] One-click **Try Demo** flow with sample manifest and fetch script
- [x] Polished UI — shared settings, welcome panel, status feedback, cohesive tabs
- [x] Demo guide and screenshot documentation

---

## v0.5 — Geofencing and workflow exports

**Goal:** Improve species accuracy and fit existing conservation pipelines.

- Optional country / region geofencing for SpeciesNet predictions
- Export to [Wildlife Insights](https://wildlifeinsights.org/) compatible formats
- Export to [iNaturalist](https://www.inaturalist.org/) observation drafts (manual review required)
- Timelapse-compatible JSON output (MegaDetector native format)
- EXIF preservation in exports

---

## v0.6 — Video and motion

**Goal:** Support common camera trap video formats.

- Short video clip upload (MP4, AVI)
- Frame sampling + detection aggregation
- Highlight frames with highest-confidence animal detections
- Export key frames with bounding boxes

**Challenge:** Video processing is memory-intensive; batch size and frame rate limits will apply.

---

## v0.7 — Acoustic monitoring (exploratory)

**Goal:** Extend BioDex beyond camera traps.

- Audio file upload (WAV, MP3)
- Integration with open bioacoustics models (e.g., BirdNET, Perch) if feasible locally
- Sync audio detections with image timestamps for multi-sensor sites

**Status:** Exploratory — depends on model size and local inference feasibility.

---

## v0.8 — Local fine-tuning UI

**Goal:** Let researchers adapt models to local species without cloud training.

- Upload labeled image crops for a target species/region
- Simple fine-tuning workflow (likely YOLO-based, building on MegaDetector ecosystem)
- Evaluate on held-out local test set
- Export custom model weights for offline use

**Challenge:** Training requires GPU and labeled data; UI must set clear expectations.

---

## Principles for all future versions

1. **Local first** — cloud features, if any, are always opt-in
2. **Conservation focus** — biodiversity protection, not surveillance
3. **Honest limitations** — document what models can and cannot do
4. **Small, readable codebase** — easy for contributors to extend
5. **Open source** — MIT license, community contributions welcome

---

## How to influence the roadmap

Open a GitHub issue with:

- Your use case (research, NGO, citizen science, land management)
- Which feature would help most
- Whether you can contribute code or test data

We prioritize features that help real conservation workflows.
