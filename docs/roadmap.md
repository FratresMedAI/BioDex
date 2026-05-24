# BioDex Roadmap

An honest look at where BioDex is headed after v1. Timelines are approximate — this is an open-source side project built for conservation utility, not enterprise speed.

---

## v1 — Current release

- [x] Single-image upload and analysis
- [x] MegaDetector v5a (MDV5A) local detection
- [x] Animal / person / vehicle bounding boxes
- [x] Blank image detection (no detections above threshold)
- [x] Confidence threshold slider
- [x] Annotated image + CSV export
- [x] Gradio web UI, fully local

---

## v0.2 — Species awareness

**Goal:** Move from "something is here" to "what species might this be?"

- Integrate [SpeciesNet](https://github.com/google/cameratrapai) or similar species classifier on top of MegaDetector animal crops
- Show top-3 species suggestions with confidence scores
- Option to run detection-only (current behavior) vs. detection + classification

**Challenge:** Species models are region-specific; we will document geographic limitations clearly.

---

## v0.3 — Video and motion

**Goal:** Support common camera trap video formats.

- Short video clip upload (MP4, AVI)
- Frame sampling + detection aggregation
- Highlight frames with highest-confidence animal detections
- Export key frames with bounding boxes

**Challenge:** Video processing is memory-intensive; batch size and frame rate limits will apply.

---

## v0.4 — Batch processing dashboard

**Goal:** Analyze folders, not just single images.

- Upload or point to a local folder of images
- Progress bar and per-image results table
- Filter view: blanks only, animals only, humans present
- Summary statistics (detection rate, species counts if v0.2 shipped)
- Bulk export of annotated images and master CSV

**Challenge:** UI responsiveness on large folders (10k+ images); may need background worker thread.

---

## v0.5 — Acoustic monitoring (exploratory)

**Goal:** Extend BioDex beyond camera traps.

- Audio file upload (WAV, MP3)
- Integration with open bioacoustics models (e.g., BirdNET, Perch) if feasible locally
- Sync audio detections with image timestamps for multi-sensor sites

**Status:** Exploratory — depends on model size and local inference feasibility.

---

## v0.6 — Export integrations

**Goal:** Fit into existing conservation workflows.

- Export to [Wildlife Insights](https://wildlifeinsights.org/) compatible formats
- Export to [iNaturalist](https://www.inaturalist.org/) observation drafts (manual review required)
- Timelapse-compatible JSON output (MegaDetector native format)
- EXIF preservation in exports

---

## v0.7 — Local fine-tuning UI

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
