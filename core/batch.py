"""
Batch analysis for multiple camera trap images.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from core.detector import analyze_single_image
from core.types import DEFAULT_SPECIES_MIN_CONFIDENCE, AnalysisResult, BatchResult, utc_now_iso

if TYPE_CHECKING:
    from PIL import Image

BatchProgressCallback = Callable[[int, int, str], None] | None


def _emit_progress(
    callback: Callable[[int, int, str], None],
    current: int,
    total: int,
    message: str,
    fraction: float,
) -> None:
    """Call batch progress hook; tolerate legacy 3-arg callbacks."""
    try:
        callback(current, total, message, fraction)  # type: ignore[misc]
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


def run_batch(
    images: list[tuple[str, Image.Image]],
    threshold: float = 0.25,
    classify_species: bool = False,
    species_min_confidence: float = DEFAULT_SPECIES_MIN_CONFIDENCE,
    progress_callback: BatchProgressCallback = None,
) -> BatchResult:
    """
    Analyze multiple images sequentially with per-image error handling.

    Args:
        images: List of ``(filename, PIL.Image)`` pairs.
        threshold: Minimum MegaDetector confidence.
        classify_species: Whether to run SpeciesNet on animal crops.
        species_min_confidence: Minimum species score before Uncertain label.
        progress_callback: Optional ``(current_index, total, message)`` hook.

    Returns:
        BatchResult with per-image results, failures, and aggregate stats.
    """
    results: list[AnalysisResult] = []
    failed: list[tuple[str, str]] = []
    total = len(images)

    for index, (filename, image) in enumerate(images, start=1):
        if progress_callback:
            _emit_progress(
                progress_callback,
                index,
                total,
                f"[{index}/{total}] {filename}",
                (index - 1) / total if total else 0.0,
            )

        def image_progress(
            message: str,
            *,
            idx: int = index,
            step: float = 0.45,
        ) -> None:
            if progress_callback:
                frac = ((idx - 1) + step) / total if total else 0.0
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
            results.append(result)
            if progress_callback:
                _emit_progress(
                    progress_callback,
                    index,
                    total,
                    f"[{index}/{total}] {filename} done",
                    index / total if total else 1.0,
                )
        except Exception as exc:
            failed.append((filename, str(exc)))
            results.append(
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
    )


__all__ = ["BatchProgressCallback", "run_batch"]
