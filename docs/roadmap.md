# BioDex Roadmap

An honest look at where BioDex is headed.

---

## v1.0 — Production baseline (complete)

**Goal:** Deliver a stable, local-first, conservation-grade baseline with strong QA and release readiness.

- [x] Pluggable model registry (`core/models/`) with MDV5A + SpeciesNet adapters
- [x] Batch chunking, cancel event, ETA progress, I/O workers
- [x] Wildlife Insights, iNaturalist, timelapse, SQLite, EcoSentinel exports
- [x] EXIF/GPS helpers and geofence config stub
- [x] Analytics: diversity index, activity heatmap
- [x] Video frame extraction and `biodex video` CLI foundations
- [x] Tabbed UI: Dashboard, Batch, Video, Analytics, Settings
- [x] Dockerfile CPU/GPU, release workflow, pre-commit

---

## v1.1 — Video, edge inference and tracking

**Goal:** Full camera-trap video workflow + a real edge path. Detailed plan: [`v1.1-plan.md`](v1.1-plan.md).

- [ ] Multi-clip batch video processing
- [ ] IOU-based detection aggregation / cross-frame tracking (count individuals, not detections)
- [ ] ONNX production edge path (promote `core/models/edge.py` stub); TensorRT deferred to v1.2
- [ ] Verified PyInstaller desktop distribution

---

## v1.2 — Acoustic monitoring (exploratory)

- [ ] BirdNET / Perch integration if feasible locally

---

## v1.3 — Local fine-tuning UI

- [ ] Upload labeled crops and fine-tune on local GPU

---

## Principles

1. **Local first** — cloud is always opt-in
2. **Conservation focus** — biodiversity, not surveillance
3. **Honest limitations** — document model boundaries
4. **Small, readable codebase** — MIT license, community welcome
