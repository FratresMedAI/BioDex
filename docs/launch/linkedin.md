# BioDex — LinkedIn launch drafts

> Status: draft for v1.0.0 GA. Add a hero image/GIF and the release link before posting.

## Post A — Launch announcement (founder voice)

Today we're releasing **BioDex v1.0.0** — local-first AI for wildlife camera-trap analysis. 🐾

Camera traps are one of conservation's most powerful tools, and also one of its biggest data
bottlenecks. A single survey can produce hundreds of thousands of images. The existing options
usually force a hard trade-off: ship sensitive imagery to a cloud API, or stand up a
data-science pipeline most field teams don't have.

BioDex removes that trade-off. Point it at a folder of images and it:

→ Detects animals, people, and vehicles with MegaDetector
→ Classifies species with SpeciesNet
→ Exports analysis-ready CSV/JSON (Wildlife Insights, iNaturalist), SQLite, and annotated images
→ Produces diversity metrics and activity heatmaps

Everything runs on your hardware. No uploads. No per-image fees. MIT-licensed and open source.

We built this for conservation biologists, ecologists, and defensive ecological monitoring teams
who need reproducible results on data that can't leave the building.

⭐ GitHub: https://github.com/FratresMedAI/BioDex

If you work in biodiversity monitoring or build on MegaDetector/SpeciesNet, I'd love your feedback.

#Conservation #AI #Wildlife #OpenSource #Biodiversity #MachineLearning #CameraTraps

---

## Post B — Technical angle (shorter)

We just shipped **BioDex v1.0.0**, an open-source, local-first wildlife camera-trap analyzer.

Under the hood:
• Pluggable model registry (MegaDetector + SpeciesNet, edge ONNX stubs)
• Batch engine with chunking, cancellation, parallel I/O, and ETA
• Tabbed Gradio UI + a scriptable Typer CLI
• Exports to Wildlife Insights, iNaturalist, SQLite, and an EcoSentinel fusion hook
• CPU/GPU Docker images and a PyInstaller desktop build

Strict quality gates (ruff, mypy --strict, pytest) pass on every commit, and it's all MIT.

The design goal: production wildlife models that run entirely offline, in a codebase small
enough to read in an afternoon.

Repo + release notes: https://github.com/FratresMedAI/BioDex/releases/tag/v1.0.0

#OpenSource #Python #ComputerVision #Conservation #AI

---

## Post C — Mission/impact angle

Conservation runs on data that often can't go to the cloud — poaching hotspots, protected
species locations, defense-adjacent monitoring sites.

That's why **BioDex** (v1.0.0, out today) is local-first by design. Drop in camera-trap photos,
get species-level detections and analysis-ready exports — without a single byte leaving your
machine.

Open source, MIT-licensed, built for impact in conservation and defensive ecological monitoring.

🔗 https://github.com/FratresMedAI/BioDex

#Conservation #ResponsibleAI #Biodiversity #OpenSource

---

## Posting tips

- Lead with the hero GIF/screenshot; LinkedIn favors native media over link previews.
- Drop the repo link as the first comment if reach is throttled by outbound links.
- Tag relevant orgs (e.g. partners, WILDLABS, model authors) where appropriate.
- Best windows: Tue–Thu mornings in your audience's timezone.
