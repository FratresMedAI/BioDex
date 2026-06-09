# BioDex — Product Hunt launch draft

> Status: draft for v1.0.0 GA. Swap in real screenshots/GIFs and the live links before posting.

## Name

BioDex

## Tagline (60 char max)

Local, private AI for wildlife camera-trap analysis

## Topics

Artificial Intelligence · Open Source · Sustainability · Developer Tools

## Thumbnail / gallery checklist

- [ ] Hero GIF: drop a camera-trap folder → annotated detections + species labels
- [ ] Screenshot: Dashboard tab with batch stats
- [ ] Screenshot: Analytics tab (diversity index + activity heatmap)
- [ ] Screenshot: CLI `biodex batch ... --classify-species` run
- [ ] Logo / icon (square, 240×240+)

## Description

BioDex is a local-first desktop and CLI tool that turns raw camera-trap photos into
structured wildlife data — no cloud upload, no per-image fees, no data leaving your machine.

Point it at a folder of images and BioDex runs MegaDetector to find animals, people, and
vehicles, then optionally classifies species with SpeciesNet. You get annotated images,
CSV/JSON exports (including Wildlife Insights and iNaturalist formats), a SQLite database,
diversity metrics, and activity heatmaps.

Built for conservation biologists, ecologists, and defensive ecological monitoring teams who
need reproducible results on sensitive data they can't send to a third-party API.

## Why we built it

Camera traps generate millions of images. Most tools are either cloud-only (a non-starter for
sensitive sites and offline field stations) or require a data-science pipeline to operate.
BioDex packages production wildlife models behind a friendly tabbed UI and a scriptable CLI,
and keeps everything on your hardware.

## What's in v1.0.0

- 🧠 Pluggable model registry — MegaDetector (MDv5a) + SpeciesNet, with edge ONNX/TensorRT stubs
- 🖥️ Tabbed UI — Dashboard, Batch, Video, Analytics, Settings (with dark mode + cancel)
- ⚡ Batch engine — chunking, cancellation, parallel I/O, ETA progress
- 🎞️ Video foundations — frame extraction + `biodex video`
- 📤 Exports — Wildlife Insights, iNaturalist, timelapse JSON, SQLite, EcoSentinel hook
- 📊 Analytics — Shannon diversity index, activity heatmaps
- 🔒 Local-first & private — optional opt-in audit log (hash-chained JSONL)
- 📦 Packaging — CPU/GPU Docker, PyInstaller desktop spec, CI/release workflows

## First comment (maker)

Hey Product Hunt 👋

I built BioDex because every camera-trap workflow I touched either shipped images to someone
else's cloud or needed a Python notebook to run. Conservation teams working on sensitive sites
(poaching hotspots, defense-adjacent monitoring) can't do either.

BioDex runs entirely on your machine — drop a folder, get annotated detections, species labels,
and analysis-ready exports. It's MIT-licensed and the codebase is intentionally small and
readable so the community can extend it.

Would love feedback from anyone doing field ecology, biodiversity monitoring, or building on
top of MegaDetector/SpeciesNet. What formats or integrations would make this part of your stack?

## Links

- GitHub: https://github.com/Fratres-X-Natura/BioDex
- Release: https://github.com/Fratres-X-Natura/BioDex/releases/tag/v1.0.0
- PyPI: https://pypi.org/project/biodex/ (pending Trusted Publisher setup — see docs/publishing.md)
