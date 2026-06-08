"""Protocol definitions for pluggable detector and classifier backends."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from PIL import Image

from core.types import DetectionRecord


@runtime_checkable
class BaseDetector(Protocol):
    """Contract for object-detection backends (e.g. MegaDetector)."""

    model_id: str

    @property
    def is_loaded(self) -> bool:
        """Return True when model weights are loaded in this process."""
        ...

    def load(self) -> None:
        """Load model weights into memory."""
        ...

    def unload(self) -> None:
        """Release model resources."""
        ...

    def predict(self, image: Image.Image, threshold: float) -> list[dict[str, Any]]:
        """Run detection and return raw detection dicts."""
        ...

    def build_records(self, raw_detections: list[dict[str, Any]]) -> list[DetectionRecord]:
        """Convert raw detections to typed DetectionRecord objects."""
        ...


@runtime_checkable
class BaseClassifier(Protocol):
    """Contract for species-classification backends (e.g. SpeciesNet)."""

    model_id: str

    @property
    def is_loaded(self) -> bool:
        """Return True when classifier weights are loaded."""
        ...

    def load(self) -> None:
        """Load classifier weights."""
        ...

    def unload(self) -> None:
        """Release classifier resources."""
        ...

    def enrich(
        self,
        image: Image.Image,
        detections: list[DetectionRecord],
        filename: str,
        *,
        species_min_confidence: float,
        geofence_region: str | None = None,
    ) -> tuple[list[DetectionRecord], list[str]]:
        """Attach species predictions to animal detections."""
        ...


__all__ = ["BaseClassifier", "BaseDetector"]
