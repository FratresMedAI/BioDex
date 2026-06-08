"""
Batch analysis for multiple camera trap images.
"""

from __future__ import annotations

import gc
import logging
import threading
from collections.abc import Callable
from typing import TYPE_CHECKING

from core.audit_log import append_audit_entry
from core.detector import analyze_single_image
from core.models.registry import unload_all
from core.progress import make_tracked_callback
from core.types import DEFAULT_SPECIES_MIN_CONFIDENCE, AnalysisResult, BatchResult, utc_now_iso

if TYPE_CHECKING:
    from PIL import Image

logger = logging.getLogger(__name__)

BatchProgressCallback = (
    Callable[[int, int, str], None]
    | Callable[[int, int, str, float], None]
    | None
)


def _emit_progress(
    callback: Callable[..., None],
    current: int,
    total: int,
    message: str,
    fraction: float,
) -> None:
    """Call batch progress hook; tolerate legacy 3-arg callbacks."""
    try:
        callback(current, total, message, fraction)
    except TypeError:
        callback(current, total, message)


def _collect_species_counts(results: list[AnalysisResult]) -> dict[str, int]:
    """Aggregate species labels across a batch (excluding Uncertain)."""
    counts: dict[str, int] = {}
    for result in results:
        for detection in result.detections:
            if not detection.species or not detection.species.label:
                continue
            label = detection.species.label
            if label.lower() == "uncertain":
                continue
            counts[label] = counts.get(label, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _build_batch_result(
    results: list[AnalysisResult],
    failed: list[tuple[str, str]],
    total: int,
    *,
    threshold: float,
    classify_species: bool,
    interrupted: bool,
) -> BatchResult:
    blank_count = sum(1 for r in results if r.is_blank and not r.error)
    return BatchResult(
        results=results,
        failed=failed,
        total_images=total,
        processed_count=len(results),
        blank_count=blank_count,
        total_detections=sum(r.total for r in results),
        animal_count=sum(r.animal_count for r in results),
        person_count=sum(r.person_count for r in results),
        vehicle_count=sum(r.vehicle_count for r in results),
        species_counts=_collect_species_counts(results),
        threshold=threshold,
        species_enabled=classify_species,
        interrupted=interrupted,
    )


def run_batch(
    images: list[tuple[str, Image.Image]],
    threshold: float = 0.25,
    classify_species: bool = False,
    species_min_confidence: float = DEFAULT_SPECIES_MIN_CONFIDENCE,
    progress_callback: BatchProgressCallback = None,
    *,
    chunk_size: int = 500,
    cancel_event: threading.Event | None = None,
    workers: int = 1,
) -> BatchResult:
    """
    Analyze multiple images sequentially with per-image error handling.

    Args:
        images: List of ``(filename, PIL.Image)`` pairs.
        threshold: Minimum MegaDetector confidence.
        classify_species: Whether to run SpeciesNet on animal crops.
        species_min_confidence: Minimum species score before Uncertain label.
        progress_callback: Optional ``(current, total, message[, fraction])`` hook.
        chunk_size: Process in chunks; unload models between chunks for large folders.
        cancel_event: When set, stop after the current image and return partial results.
        workers: Parallel I/O workers for pre-loading (inference stays single-process).

    Returns:
        BatchResult with per-image results, failures, and aggregate stats.
    """
    total = len(images)
    if total == 0:
        return _build_batch_result([], [], 0, threshold=threshold, classify_species=classify_species, interrupted=False)

    tracker, tracked_emit = make_tracked_callback(
        progress_callback,  # type: ignore[arg-type]
        total,
    )

    all_results: list[AnalysisResult] = []
    all_failed: list[tuple[str, str]] = []
    interrupted = False

    for chunk_start in range(0, total, chunk_size):
        chunk = images[chunk_start : chunk_start + chunk_size]
        if chunk_start > 0:
            logger.info("Chunk complete; unloading models and collecting garbage.")
            unload_all()
            gc.collect()

        for offset, (filename, image) in enumerate(chunk):
            global_index = chunk_start + offset + 1

            if cancel_event is not None and cancel_event.is_set():
                interrupted = True
                logger.info("Batch cancelled at image %s/%s", global_index - 1, total)
                break

            tracked_emit(global_index - 1, f"[{global_index}/{total}] {filename}")

            def image_progress(
                message: str,
                *,
                idx: int = global_index,
                step: float = 0.45,
            ) -> None:
                frac = ((idx - 1) + step) / total if total else 0.0
                if progress_callback:
                    _emit_progress(
                        progress_callback,
                        idx,
                        total,
                        f"[{idx}/{total}] {message}",
                        frac,
                    )

            try:
                result = analyze_single_image(
                    image,
                    threshold=threshold,
                    classify_species=classify_species,
                    filename=filename,
                    species_min_confidence=species_min_confidence,
                    progress_callback=image_progress,
                )
                all_results.append(result)
                tracked_emit(global_index, f"[{global_index}/{total}] {filename} done")
            except Exception as exc:
                all_failed.append((filename, str(exc)))
                all_results.append(
                    AnalysisResult(
                        detections=[],
                        total=0,
                        animal_count=0,
                        person_count=0,
                        vehicle_count=0,
                        is_blank=True,
                        threshold=threshold,
                        species_enabled=classify_species,
                        filename=filename,
                        summary=f"Analysis failed for {filename}: {exc}",
                        analyzed_at=utc_now_iso(),
                        warnings=[str(exc)],
                        error=str(exc),
                    )
                )

        if interrupted:
            break

    append_audit_entry(
        "batch_complete",
        {
            "total_images": total,
            "processed": len(all_results),
            "failed": len(all_failed),
            "interrupted": interrupted,
            "species_enabled": classify_species,
        },
    )

    return _build_batch_result(
        all_results,
        all_failed,
        total,
        threshold=threshold,
        classify_species=classify_species,
        interrupted=interrupted,
    )


def run_batch_from_paths(
    path_pairs: list[tuple[str, str]],
    *,
    threshold: float = 0.25,
    classify_species: bool = False,
    species_min_confidence: float = DEFAULT_SPECIES_MIN_CONFIDENCE,
    progress_callback: BatchProgressCallback = None,
    chunk_size: int | None = None,
    workers: int = 1,
    cancel_event: threading.Event | None = None,
) -> BatchResult:
    """
    Load images from disk and run batch analysis.

    ``workers`` parallelizes image loading only; inference stays single-process.
    """
    from concurrent.futures import ThreadPoolExecutor

    from PIL import Image

    effective_chunk = chunk_size if chunk_size is not None else 500

    def load_one(name_path: tuple[str, str]) -> tuple[str, Image.Image]:
        name, path_str = name_path
        with Image.open(path_str) as img:
            return name, img.convert("RGB")

    if workers > 1:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            images = list(pool.map(load_one, path_pairs))
    else:
        images = [load_one(pair) for pair in path_pairs]

    return run_batch(
        images,
        threshold=threshold,
        classify_species=classify_species,
        species_min_confidence=species_min_confidence,
        progress_callback=progress_callback,
        chunk_size=effective_chunk,
        cancel_event=cancel_event,
        workers=workers,
    )


__all__ = ["BatchProgressCallback", "run_batch", "run_batch_from_paths"]
