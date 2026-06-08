# BioDex Roadmap

An honest look at where BioDex is headed.

---

## v0.5 — Geofencing, exports, video foundations (complete)

**Goal:** Pluggable models, conservation pipeline exports, and video prep for v0.6.

- [x] Pluggable model registry (`core/models/`) with MDV5A + SpeciesNet adapters
- [x] Batch chunking, cancel event, ETA progress, I/O workers
- [x] Wildlife Insights, iNaturalist, timelapse, SQLite, EcoSentinel exports
- [x] EXIF/GPS helpers and geofence config stub
- [x] Analytics: diversity index, activity heatmap
- [x] Video frame extraction and `biodex video` CLI
- [x] Tabbed UI: Dashboard, Batch, Video, Analytics, Settings
- [x] Dockerfile CPU/GPU, release workflow, pre-commit

---

## v0.6 — Video and motion

**Goal:** Full camera-trap video workflow.

- [ ] Multi-clip batch video processing
- [ ] IOU-based detection aggregation across frames
- [ ] ONNX/TensorRT production edge paths
- [ ] Verified PyInstaller desktop distribution

---

## v0.7 — Acoustic monitoring (exploratory)

- [ ] BirdNET / Perch integration if feasible locally

---

## v0.8 — Local fine-tuning UI

- [ ] Upload labeled crops and fine-tune on local GPU

---

## Principles

1. **Local first** — cloud is always opt-in
2. **Conservation focus** — biodiversity, not surveillance
3. **Honest limitations** — document model boundaries
4. **Small, readable codebase** — MIT license, community welcome
