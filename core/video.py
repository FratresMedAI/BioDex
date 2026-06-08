"""Video frame extraction and analysis foundations (v0.6 prep)."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from PIL import Image

from core.audit_log import append_audit_entry
from core.batch import run_batch
from core.types import AnalysisResult, VideoResult, bbox_area

logger = logging.getLogger(__name__)

VIDEO_SUFFIXES = {".mp4", ".avi", ".mov", ".mkv", ".webm"}


def _require_video_extra() -> None:
    try:
        import cv2  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "Video support requires OpenCV. Install with: pip install 'biodex[video]'"
        ) from exc


def extract_frames(
    path: Path,
    *,
    fps: float | None = None,
    max_frames: int = 300,
) -> list[tuple[int, Image.Image]]:
    """
    Sample frames from a video file.

    Args:
        path: Path to video clip.
        fps: Target sampling rate; ``None`` uses native FPS capped by ``max_frames``.
        max_frames: Maximum frames to extract.

    Returns:
        List of ``(frame_index, PIL.Image)`` tuples in RGB.
    """
    _require_video_extra()
    import cv2

    if not path.is_file():
        raise ValueError(f"Video file not found: {path}")

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {path}")

    native_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    sample_every = 1
    if fps is not None and fps > 0:
        sample_every = max(1, int(round(native_fps / fps)))

    frames: list[tuple[int, Image.Image]] = []
    index = 0
    read_index = 0

    try:
        while len(frames) < max_frames:
            ok, frame = cap.read()
            if not ok:
                break
            if read_index % sample_every == 0:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil = Image.fromarray(rgb)
                frames.append((index, pil))
                index += 1
            read_index += 1
            if total_frames and read_index >= total_frames:
                break
    finally:
        cap.release()

    if not frames:
        raise ValueError(f"No frames extracted from {path}")
    return frames


def _iou(a: list[float], b: list[float]) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ax2, ay2 = ax + aw, ay + ah
    bx2, by2 = bx + bw, by + bh
    ix0, iy0 = max(ax, bx), max(ay, by)
    ix1, iy1 = min(ax2, bx2), min(ay2, by2)
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    inter = (ix1 - ix0) * (iy1 - iy0)
    union = aw * ah + bw * bh - inter
    return inter / union if union > 0 else 0.0


def aggregate_detections(frames: list[AnalysisResult]) -> list[tuple[int, AnalysisResult]]:
    """
    Select key frames with highest-confidence animal detections.

    Simple IOU stub: picks frames with animals sorted by max detection confidence.
    """
    scored: list[tuple[int, AnalysisResult, float]] = []
    for frame_index, result in enumerate(frames):
        if result.is_blank or not result.detections:
            continue
        best = max(result.detections, key=lambda d: d.confidence)
        scored.append((frame_index, result, best.confidence))

    scored.sort(key=lambda item: (-item[2], -item[1].animal_count))
    return [(idx, res) for idx, res, _ in scored[: min(10, len(scored))]]


def analyze_video(
    path: Path,
    *,
    threshold: float = 0.25,
    classify_species: bool = False,
    fps: float | None = 1.0,
    max_frames: int = 300,
    cancel_event: object | None = None,
    progress_callback: object | None = None,
    **batch_kwargs: object,
) -> VideoResult:
    """Extract frames and run batch analysis on a video clip."""
    sampled = extract_frames(path, fps=fps, max_frames=max_frames)
    pairs = [(f"frame_{idx:06d}.jpg", img) for idx, img in sampled]

    batch = run_batch(
        pairs,
        threshold=threshold,
        classify_species=classify_species,
        progress_callback=progress_callback,  # type: ignore[arg-type]
        cancel_event=cancel_event,  # type: ignore[arg-type]
        **batch_kwargs,  # type: ignore[arg-type]
    )

    key_frames = aggregate_detections(batch.results)
    timeline_path = export_video_timeline(
        VideoResult(
            source_path=path,
            frames=batch.results,
            key_frames=key_frames,
            timeline_json=None,
            species_counts=batch.species_counts,
            total_frames=len(batch.results),
            fps_sampled=fps,
            interrupted=batch.interrupted,
        ),
        path.parent,
    )

    result = VideoResult(
        source_path=path,
        frames=batch.results,
        key_frames=key_frames,
        timeline_json=timeline_path,
        species_counts=batch.species_counts,
        total_frames=len(batch.results),
        fps_sampled=fps,
        interrupted=batch.interrupted,
    )

    append_audit_entry(
        "video_analyzed",
        {
            "source": str(path),
            "frames": result.total_frames,
            "animals": sum(r.animal_count for r in result.frames),
            "interrupted": result.interrupted,
        },
    )
    return result


def export_video_timeline(result: VideoResult, out_dir: Path) -> Path:
    """Write JSON timeline and return its path."""
    out_dir.mkdir(parents=True, exist_ok=True)
    timeline_path = out_dir / f"{result.source_path.stem}_timeline.json"

    timeline = {
        "source": str(result.source_path),
        "total_frames": result.total_frames,
        "fps_sampled": result.fps_sampled,
        "species_counts": result.species_counts,
        "interrupted": result.interrupted,
        "frames": [
            {
                "index": index,
                "filename": frame.filename,
                "animal_count": frame.animal_count,
                "is_blank": frame.is_blank,
                "detections": [
                    {
                        "category": d.category,
                        "confidence": d.confidence,
                        "bbox": d.bbox,
                        "bbox_area": bbox_area(d.bbox),
                        "species": d.species.label if d.species else None,
                    }
                    for d in frame.detections
                ],
            }
            for index, frame in enumerate(result.frames)
        ],
        "key_frames": [
            {
                "index": idx,
                "filename": frame.filename,
                "animal_count": frame.animal_count,
            }
            for idx, frame in result.key_frames
        ],
    }

    timeline_path.write_text(json.dumps(timeline, indent=2), encoding="utf-8")
    return timeline_path


__all__ = [
    "VIDEO_SUFFIXES",
    "aggregate_detections",
    "analyze_video",
    "export_video_timeline",
    "extract_frames",
]
