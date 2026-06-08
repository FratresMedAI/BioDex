"""Edge inference stubs (ONNX / TensorRT) — opt-in via ``[edge]`` extra."""

from __future__ import annotations

from PIL import Image

from core.types import DetectionRecord


class ONNXDetectorAdapter:
    """ONNX Runtime detector stub — requires ``pip install biodex[edge]``."""

    model_id = "onnx"

    def __init__(self) -> None:
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def load(self) -> None:
        try:
            import onnxruntime  # noqa: F401
        except ImportError as exc:
            raise NotImplementedError(
                "ONNX edge inference is not available. "
                "Install with: pip install 'biodex[edge]'"
            ) from exc
        raise NotImplementedError(
            "ONNX detector adapter is a v0.5 stub. Use MDV5A (default) for production."
        )

    def unload(self) -> None:
        self._loaded = False

    def predict(self, image: Image.Image, threshold: float) -> list[dict[str, object]]:
        raise NotImplementedError("ONNX detector not implemented in v0.5.")

    def build_records(self, raw_detections: list[dict[str, object]]) -> list[DetectionRecord]:
        raise NotImplementedError("ONNX detector not implemented in v0.5.")


class TensorRTDetectorAdapter:
    """TensorRT detector stub — requires CUDA and edge extra."""

    model_id = "tensorrt"

    def __init__(self) -> None:
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def load(self) -> None:
        raise NotImplementedError(
            "TensorRT edge inference is planned for v0.6+. "
            "Use MDV5A (default) or install biodex[edge] for ONNX stubs."
        )

    def unload(self) -> None:
        self._loaded = False

    def predict(self, image: Image.Image, threshold: float) -> list[dict[str, object]]:
        raise NotImplementedError("TensorRT detector not implemented in v0.5.")

    def build_records(self, raw_detections: list[dict[str, object]]) -> list[DetectionRecord]:
        raise NotImplementedError("TensorRT detector not implemented in v0.5.")


__all__ = ["ONNXDetectorAdapter", "TensorRTDetectorAdapter"]
