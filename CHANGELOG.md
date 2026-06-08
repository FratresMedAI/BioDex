# Changelog

All notable changes to BioDex are documented here.

## [0.5.0] — 2025-06-08

### Added

- **Pluggable model architecture** — `core/models/` registry with MegaDetector and SpeciesNet adapters; edge ONNX/TensorRT stubs
- **ModelSettings** — env-driven config (`BIODEX_DETECTOR_MODEL`, `BIODEX_TORCH_COMPILE`, `BIODEX_GEOFENCE_REGION`, etc.)
- **Batch performance** — chunking, cancel event, I/O workers, ETA progress (`core/progress.py`)
- **Video foundations** — `core/video.py` frame extraction, `VideoResult`, `biodex video` CLI (requires `[video]` extra)
- **Advanced exports** — Wildlife Insights CSV, iNaturalist drafts, timelapse JSON, SQLite, EcoSentinel hook
- **Analytics** — diversity index, activity heatmap (`[analytics]` extra)
- **Audit log stub** — opt-in hash-chained JSONL (`BIODEX_AUDIT_LOG=1`)
- **EXIF/GPS** — `core/exif_utils.py` for export metadata and geofencing fallback
- **Tabbed UI** — Dashboard, Batch, Video, Analytics, Settings tabs with dark mode and cancel button
- **Packaging** — Dockerfile (CPU/GPU), release workflow, pre-commit hooks
- **Optional extras** — `video`, `analytics`, `edge`, `all`

### Changed

- `detector.py` and `classifier.py` refactored as thin facades over the model registry
- CLI adds `--chunk-size`, `--workers`, `--torch-compile`
- JSON exports include `human_review` and `review_notes` fields
- `BatchResult.interrupted` flag for cancelled runs

### Backwards compatibility

- All symbols in `core/__init__.py` remain importable with identical default behavior (MDV5A + SpeciesNet)
- `build_app()` and `launch_app()` signatures unchanged

## [0.4.x] — prior releases

See git history for v0.4 batch CLI, species tiers, and field-review UI.
