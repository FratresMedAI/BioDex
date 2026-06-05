# Architecture decision: `core/` package name

BioDex uses a top-level package named **`core`** instead of **`utils`**.

## Context

MegaDetector’s YOLOv5 backend imports modules such as `utils.general` and
`utils.datasets` from the **YOLOv5** tree bundled with megadetector. If BioDex
also shipped a top-level `utils/` package, Python would resolve `utils` to our
code first and **break MegaDetector model loading**.

## Decision

Keep pipeline logic in `core/` (detector, classifier, exports, batch, cli).

## Consequences

- Import paths are `from core.detector import …` rather than `from utils.…`.
- Do not add a top-level `utils/` package to this repository.
