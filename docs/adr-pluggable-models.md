# ADR: Pluggable Model Architecture (v0.5)

## Status

Accepted — implemented in BioDex v0.5.0

## Context

BioDex v0.4 hardwired MegaDetector (`MDV5A`) and SpeciesNet as module-level singletons in `core/detector.py` and `core/classifier.py`. This blocked:

- Swapping detector/classifier backends (MDv5b, ONNX, custom weights)
- LRU eviction for memory-constrained edge devices
- Opt-in `torch.compile` without touching call sites
- Test isolation without monkeypatching private globals

## Decision

Introduce `core/models/` with:

1. **`Protocol`-based contracts** (`BaseDetector`, `BaseClassifier`) — mypy strict-friendly, no inheritance required for adapters
2. **Registry pattern** — `@register_detector` / `@register_classifier` decorators; `get_detector(id)` / `get_classifier(id)` with LRU cache
3. **Thin facades** — existing `core/detector.py` and `core/classifier.py` delegate to the registry; public API unchanged
4. **Default registrations at import** — `MDV5A` → `MegaDetectorAdapter`, `speciesnet` → `SpeciesNetAdapter`

## Backwards compatibility

| Symbol | v0.4 behavior | v0.5 behavior |
|--------|---------------|---------------|
| `get_detector()` | Returns MegaDetector model | Returns same model via adapter (default `MDV5A`) |
| `analyze_single_image()` | MD + optional SpeciesNet | Same; optional `detector=` / `classifier=` kwargs |
| `MODEL_ID` | `"MDV5A"` | Unchanged constant |
| `core/__init__.py` exports | All present | All present |

## Future entry points

- **MDv5b** — register as `register_detector("MDV5B", MegaDetectorAdapter)` with different `model_id`
- **ONNX / TensorRT** — stubs in `core/models/edge.py`; production paths deferred to v0.6+
- **BirdNET** — separate acoustic adapter (v0.7)

## Consequences

- **Positive:** Testable adapters, configurable via env vars, clear extension point
- **Negative:** Extra indirection layer; registry must be imported before use (handled in `core/models/__init__.py`)
- **Mitigation:** Package named `core.models` (not top-level `models`) to avoid shadowing MegaDetector YOLOv5 `utils` imports

## References

- [MegaDetector](https://github.com/agentmorris/MegaDetector)
- [SpeciesNet](https://github.com/google/cameratrapai)
- BioDex `core/config.py` — `ModelSettings`
