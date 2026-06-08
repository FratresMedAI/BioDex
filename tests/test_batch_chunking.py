"""Tests for batch chunking and cancel event."""

from __future__ import annotations

import threading

import pytest
from core.batch import run_batch
from core.types import AnalysisResult
from PIL import Image


def _fake_result(filename: str) -> AnalysisResult:
    return AnalysisResult(
        detections=[],
        total=0,
        animal_count=0,
        person_count=0,
        vehicle_count=0,
        is_blank=True,
        threshold=0.25,
        species_enabled=False,
        filename=filename,
        summary="blank",
    )


def test_batch_cancel_event(monkeypatch: pytest.MonkeyPatch) -> None:
    cancel = threading.Event()
    images = [(f"img_{i}.jpg", Image.new("RGB", (8, 8))) for i in range(5)]

    def fake_analyze(*_args: object, **_kwargs: object) -> AnalysisResult:
        if fake_analyze.calls >= 2:  # type: ignore[attr-defined]
            cancel.set()
        fake_analyze.calls += 1  # type: ignore[attr-defined]
        return _fake_result(f"img_{fake_analyze.calls}.jpg")  # type: ignore[attr-defined]

    fake_analyze.calls = 0  # type: ignore[attr-defined]
    monkeypatch.setattr("core.batch.analyze_single_image", fake_analyze)

    batch = run_batch(images, cancel_event=cancel, chunk_size=2)
    assert batch.interrupted is True
    assert batch.processed_count >= 2


def test_batch_empty() -> None:
    batch = run_batch([])
    assert batch.total_images == 0
    assert batch.interrupted is False
