"""Tests for analytics module."""

from __future__ import annotations

from core.analytics import compute_diversity_index, population_trend_stub
from core.types import BatchResult


def test_compute_diversity_index_empty() -> None:
    result = compute_diversity_index({})
    assert result["shannon"] == 0.0
    assert result["richness"] == 0.0


def test_compute_diversity_index_species() -> None:
    result = compute_diversity_index({"Deer": 5, "Fox": 3})
    assert result["richness"] == 2.0
    assert result["shannon"] > 0


def test_population_trend_stub() -> None:
    batch = BatchResult(
        results=[],
        failed=[],
        total_images=0,
        processed_count=0,
        blank_count=0,
        total_detections=0,
        animal_count=3,
        person_count=0,
        vehicle_count=0,
    )
    stub = population_trend_stub([batch])
    assert stub["status"] == "stub"
    assert stub["animal_totals"] == [3]
