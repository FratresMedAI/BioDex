"""MegaDetector v5a adapter for the pluggable model registry."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import numpy.typing as npt
from PIL import Image, ImageOps

from core.config import get_model_settings
from core.types import MODEL_ID, DetectionRecord, get_category_label

logger = logging.getLogger(__name__)


def prepare_camera_trap_image(image: Image.Image) -> Image.Image:
    """
    Normalize a camera trap image for detection and display.

    Fixes EXIF orientation (common on trail cameras), validates pixels,
    and converts to RGB without downscaling.
    """
    if not isinstance(image, Image.Image):
        raise ValueError("Expected a PIL Image for analysis.")

    try:
        image.load()
    except Exception as exc:
        raise ValueError("Could not read the uploaded image. It may be corrupt.") from exc

    image = ImageOps.exif_transpose(image)
    if image.mode != "RGB":
        try:
            image = image.convert("RGB")
        except Exception as exc:
            raise ValueError("Could not convert image to RGB.") from exc

    width, height = image.size
    if width <= 0 or height <= 0:
        raise ValueError("Image has invalid dimensions (width and height must be > 0).")
    return image


def pil_to_numpy(image: Image.Image) -> npt.NDArray[Any]:
    """Convert PIL RGB image to numpy array expected by MegaDetector."""
    return np.array(image)


def build_detection_records(raw_detections: list[dict[str, Any]]) -> list[DetectionRecord]:
    """Convert MegaDetector dicts into typed DetectionRecord objects."""
    records: list[DetectionRecord] = []
    for index, detection in enumerate(raw_detections, start=1):
        category_id = str(detection.get("category", ""))
        bbox = detection.get("bbox") or [0.0, 0.0, 0.0, 0.0]
        records.append(
            DetectionRecord(
                detection_id=index,
                category_id=category_id,
                category=get_category_label(category_id),
                confidence=float(detection.get("conf", 0.0)),
                bbox=list(bbox),
            )
        )
    return records


class MegaDetectorAdapter:
    """MegaDetector MDV5A backend implementing BaseDetector."""

    model_id = MODEL_ID

    def __init__(self) -> None:
        self._model: Any = None

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def load(self) -> None:
        if self._model is not None:
            return
        try:
            from megadetector.detection import run_detector

            logger.info("Loading MegaDetector model %s…", self.model_id)
            self._model = run_detector.load_detector(self.model_id)
            settings = get_model_settings()
            if settings.torch_compile:
                self._maybe_compile()
            logger.info("MegaDetector ready.")
        except Exception as exc:
            logger.exception("MegaDetector load failed")
            raise RuntimeError(
                "Failed to load MegaDetector. If this is your first run, "
                "model weights may still be downloading (~280 MB). "
                f"Details: {exc}"
            ) from exc

    def _maybe_compile(self) -> None:
        """Apply torch.compile when enabled and PyTorch >= 2.0."""
        try:
            import torch

            if not hasattr(torch, "compile"):
                logger.warning("torch.compile unavailable; running eager mode.")
                return
            if self._model is None:
                return
            inner = getattr(self._model, "model", self._model)
            compiled = torch.compile(inner)
            if hasattr(self._model, "model"):
                self._model.model = compiled
            else:
                self._model = compiled
            logger.info("Applied torch.compile to MegaDetector.")
        except Exception as exc:
            logger.warning("torch.compile failed; falling back to eager: %s", exc)

    def unload(self) -> None:
        self._model = None

    def predict(self, image: Image.Image, threshold: float) -> list[dict[str, Any]]:
        if self._model is None:
            self.load()
        assert self._model is not None
        try:
            raw = self._model.generate_detections_one_image(
                pil_to_numpy(image),
                detection_threshold=threshold,
            )
        except Exception as exc:
            logger.exception("MegaDetector inference failed")
            raise RuntimeError(
                "MegaDetector inference failed. Check model weights and image format. "
                f"Details: {exc}"
            ) from exc
        all_detections: list[dict[str, Any]] = raw.get("detections", [])
        return [d for d in all_detections if float(d.get("conf", 0.0)) >= threshold]

    def build_records(self, raw_detections: list[dict[str, Any]]) -> list[DetectionRecord]:
        return build_detection_records(raw_detections)


__all__ = [
    "MegaDetectorAdapter",
    "build_detection_records",
    "pil_to_numpy",
    "prepare_camera_trap_image",
]
