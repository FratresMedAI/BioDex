# Changelog

All notable changes to BioDex are documented here.

## [1.0.0] — 2026-06-08

### Added

- General-availability release line for BioDex with local-first camera-trap analysis workflows
- Stable tabbed UI workflow (Dashboard, Batch, Video, Analytics, Settings) and export pipeline coverage
- Production packaging path (CPU/GPU Dockerfiles, release workflow, pre-commit hooks)

### Changed

- Version bumped from `0.5.0` to `1.0.0` in runtime metadata and release documentation
- Roadmap and README updated to reflect a v1 baseline and post-1.0 planning

### Reliability

- Full quality gates pass: pytest (`not slow`), ruff, mypy (`core`, `app.py`, `ui`), and `build_app()` smoke check
- Default behavior remains backwards-compatible (`MDV5A` detector + optional SpeciesNet classification)
- CI/release hardening: package build job, pre-commit checks in CI, and Docker health checks
- Added release documentation artifacts: `CITATION.cff`, `CONTRIBUTING.md`, `SECURITY.md`

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
