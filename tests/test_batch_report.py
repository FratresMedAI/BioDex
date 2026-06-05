"""Fast tests for core.batch_report."""

from __future__ import annotations

from pathlib import Path

from core.batch_report import format_batch_report
from core.types import AnalysisResult, BatchResult


def test_format_batch_report_includes_failures_and_species() -> None:
    batch = BatchResult(
        results=[
            AnalysisResult(
                detections=[],
                total=2,
                animal_count=2,
                person_count=0,
                vehicle_count=0,
                is_blank=False,
                threshold=0.25,
                species_enabled=True,
                filename="a.jpg",
                summary="ok",
            )
        ],
        failed=[("bad.jpg", "read error")],
        total_images=2,
        processed_count=2,
        blank_count=0,
        total_detections=2,
        animal_count=2,
        person_count=0,
        vehicle_count=0,
        species_counts={"Fox": 2},
        threshold=0.25,
        species_enabled=True,
    )
    text = format_batch_report(
        batch,
        input_dir=Path("/data/in"),
        output_dir=Path("/data/out"),
        summary_csv=Path("/data/out/batch_summary.csv"),
        summary_json=Path("/data/out/batch_summary.json"),
        annotated_zip=Path("/data/out/batch_annotated.zip"),
    )
    assert "=== BioDex Batch Report ===" in text
    assert "bad.jpg: read error" in text
    assert "Species counts:" in text
    assert "=== END ===" in text
