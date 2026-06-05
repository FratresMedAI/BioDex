"""Human-readable batch summary reports for CLI and exports."""

from __future__ import annotations

from pathlib import Path

from core.types import BIODEX_VERSION, BatchResult


def format_batch_report(
    batch: BatchResult,
    *,
    input_dir: Path,
    output_dir: Path,
    summary_csv: Path,
    summary_json: Path,
    annotated_zip: Path | None = None,
) -> str:
    """Build a plain-text aggregate report for batch folder runs."""
    blank_rate = (batch.blank_count / batch.total_images * 100) if batch.total_images else 0.0
    multi_animal_images = sum(1 for result in batch.results if result.animal_count >= 2)

    lines = [
        "=== BioDex Batch Report ===",
        f"Version: {BIODEX_VERSION}",
        f"Input folder: {input_dir.resolve()}",
        f"Output folder: {output_dir.resolve()}",
        f"Images processed: {batch.total_images}",
        f"Blanks: {batch.blank_count} ({blank_rate:.1f}%)",
        f"Failed: {len(batch.failed)}",
        f"Total detections: {batch.total_detections}",
        (
            f"Animals: {batch.animal_count} | People: {batch.person_count} "
            f"| Vehicles: {batch.vehicle_count}"
        ),
        f"Images with 2+ animals: {multi_animal_images}",
    ]

    if batch.species_enabled and batch.species_counts:
        top_species = sorted(
            batch.species_counts.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:10]
        lines.append(f"Species counts: {dict(batch.species_counts)}")
        lines.append(
            "Top species: "
            + ", ".join(f"{name} ({count})" for name, count in top_species)
        )

    if batch.failed:
        lines.append("Failures:")
        for filename, message in batch.failed[:20]:
            lines.append(f"  - {filename}: {message}")
        if len(batch.failed) > 20:
            lines.append(f"  … and {len(batch.failed) - 20} more")

    preview = batch.results[:15]
    per_image = ", ".join(
        f"{result.filename} -> {result.animal_count}" for result in preview
    )
    if len(batch.results) > len(preview):
        per_image += f", … (+{len(batch.results) - len(preview)} more)"
    lines.append(f"Per-image (sample): {per_image}")
    lines.append(f"Master CSV: {summary_csv.resolve()}")
    lines.append(f"Master JSON: {summary_json.resolve()}")
    if annotated_zip is not None:
        lines.append(f"Annotated ZIP: {annotated_zip.resolve()}")
    lines.append("=== END ===")
    return "\n".join(lines)


__all__ = ["format_batch_report"]
