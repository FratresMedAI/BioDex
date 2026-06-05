"""
Export helpers for BioDex detection results (CSV, JSON, ZIP bundles, and images).
"""

from __future__ import annotations

import json
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import pandas as pd
from PIL import Image

from core.types import (
    BIODEX_VERSION,
    AnalysisResult,
    BatchResult,
    DetectionRecord,
    SpeciesPrediction,
    format_species_alternatives,
)


def _format_top3(species: SpeciesPrediction | None) -> str:
    if not species or not species.top3:
        return ""
    return "|".join(f"{label}:{score:.4f}" for label, score in species.top3)


def _base_row_fields(result: AnalysisResult) -> dict[str, Any]:
    return {
        "filename": result.filename,
        "image_width": result.image_width,
        "image_height": result.image_height,
        "analyzed_at": result.analyzed_at,
        "is_blank": result.is_blank,
        "threshold": result.threshold,
        "species_enabled": result.species_enabled,
        "biodex_version": BIODEX_VERSION,
    }


def _detection_to_row(result: AnalysisResult, detection: DetectionRecord) -> dict[str, Any]:
    bbox = detection.bbox
    species = detection.species
    row = {
        **_base_row_fields(result),
        "detection_id": detection.detection_id,
        "category": detection.category,
        "category_id": detection.category_id,
        "confidence": round(detection.confidence, 4),
        "xmin": bbox[0],
        "ymin": bbox[1],
        "width": bbox[2],
        "height": bbox[3],
        "species": species.label if species else "",
        "species_confidence": round(species.confidence, 4) if species else "",
        "species_tier": species.confidence_tier if species else "",
        "species_alternatives": format_species_alternatives(species),
        "species_top3": _format_top3(species),
        "error": result.error,
    }
    return row


def _blank_summary_row(result: AnalysisResult) -> dict[str, Any]:
    return {
        **_base_row_fields(result),
        "detection_id": "",
        "category": "",
        "category_id": "",
        "confidence": "",
        "xmin": "",
        "ymin": "",
        "width": "",
        "height": "",
        "species": "",
        "species_confidence": "",
        "species_tier": "",
        "species_alternatives": "",
        "species_top3": "",
        "error": result.error,
    }


CSV_COLUMNS = [
    "filename",
    "detection_id",
    "category",
    "category_id",
    "confidence",
    "xmin",
    "ymin",
    "width",
    "height",
    "species",
    "species_confidence",
    "species_tier",
    "species_alternatives",
    "species_top3",
    "image_width",
    "image_height",
    "analyzed_at",
    "is_blank",
    "threshold",
    "species_enabled",
    "biodex_version",
    "error",
]


def detections_to_csv(result: AnalysisResult) -> str:
    """Write detections to a temporary CSV file and return its path."""
    if result.detections:
        rows = [_detection_to_row(result, detection) for detection in result.detections]
    else:
        rows = [_blank_summary_row(result)]

    df = pd.DataFrame(rows, columns=CSV_COLUMNS)

    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv",
        prefix="biodex_detections_",
        delete=False,
        newline="",
    )
    df.to_csv(tmp.name, index=False)
    tmp.close()
    return tmp.name


def batch_to_csv(batch: BatchResult) -> str:
    """Write all batch results to a single master CSV file."""
    rows: list[dict[str, Any]] = []
    for result in batch.results:
        if result.detections:
            rows.extend(_detection_to_row(result, d) for d in result.detections)
        else:
            rows.append(_blank_summary_row(result))

    df = pd.DataFrame(rows, columns=CSV_COLUMNS)
    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv",
        prefix="biodex_batch_",
        delete=False,
        newline="",
    )
    df.to_csv(tmp.name, index=False)
    tmp.close()
    return tmp.name


def _detection_to_json_dict(detection: DetectionRecord) -> dict[str, Any]:
    species_payload = None
    if detection.species:
        species_payload = {
            "label": detection.species.label,
            "confidence": detection.species.confidence,
            "confidence_tier": detection.species.confidence_tier,
            "raw_label": detection.species.raw_label,
            "alternatives": format_species_alternatives(detection.species),
            "top3": [
                {"label": label, "confidence": score}
                for label, score in detection.species.top3
            ],
        }

    xmin, ymin, width, height = detection.bbox
    return {
        "detection_id": detection.detection_id,
        "category": detection.category,
        "category_id": detection.category_id,
        "confidence": detection.confidence,
        "bbox": {
            "xmin": xmin,
            "ymin": ymin,
            "width": width,
            "height": height,
        },
        "species": species_payload,
    }


def _result_to_json_payload(result: AnalysisResult) -> dict[str, Any]:
    return {
        "biodex_version": BIODEX_VERSION,
        "filename": result.filename,
        "image_width": result.image_width,
        "image_height": result.image_height,
        "analyzed_at": result.analyzed_at,
        "threshold": result.threshold,
        "species_enabled": result.species_enabled,
        "is_blank": result.is_blank,
        "summary": result.summary,
        "warnings": result.warnings,
        "error": result.error,
        "model_id": result.model_id,
        "inference_ms": result.inference_ms,
        "timestamp": result.timestamp,
        "counts": {
            "total": result.total,
            "animals": result.animal_count,
            "people": result.person_count,
            "vehicles": result.vehicle_count,
        },
        "detections": [_detection_to_json_dict(d) for d in result.detections],
    }


def export_json(result: AnalysisResult) -> str:
    """Write analysis results to a temporary JSON file and return its path."""
    payload = _result_to_json_payload(result)

    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        prefix="biodex_results_",
        delete=False,
        encoding="utf-8",
    )
    json.dump(payload, tmp, indent=2)
    tmp.close()
    return tmp.name


def export_batch_json(batch: BatchResult) -> str:
    """Write batch analysis results to a temporary JSON file."""
    payload = {
        "biodex_version": BIODEX_VERSION,
        "total_images": batch.total_images,
        "processed_count": batch.processed_count,
        "failed_count": len(batch.failed),
        "threshold": batch.threshold,
        "species_enabled": batch.species_enabled,
        "summary": {
            "blank_count": batch.blank_count,
            "total_detections": batch.total_detections,
            "animals": batch.animal_count,
            "people": batch.person_count,
            "vehicles": batch.vehicle_count,
            "species_counts": batch.species_counts,
        },
        "failed": [{"filename": name, "error": err} for name, err in batch.failed],
        "results": [_result_to_json_payload(r) for r in batch.results],
    }

    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        prefix="biodex_batch_",
        delete=False,
        encoding="utf-8",
    )
    json.dump(payload, tmp, indent=2)
    tmp.close()
    return tmp.name


def save_annotated_image(image: Image.Image, filename_prefix: str = "biodex_annotated_") -> str:
    """Save annotated image to a temporary PNG and return its path."""
    tmp = tempfile.NamedTemporaryFile(
        suffix=".png",
        prefix=filename_prefix,
        delete=False,
    )
    tmp.close()
    image.save(tmp.name, format="PNG")
    return tmp.name


def export_bundle(result: AnalysisResult, annotated_image: Image.Image) -> str:
    """
    Create a ZIP bundle containing annotated PNG, CSV, and JSON for one analysis.
    """
    annotated_path = save_annotated_image(annotated_image)
    csv_path = detections_to_csv(result)
    json_path = export_json(result)

    tmp = tempfile.NamedTemporaryFile(
        suffix=".zip",
        prefix="biodex_bundle_",
        delete=False,
    )
    tmp.close()

    stem = Path(result.filename).stem or "analysis"
    with zipfile.ZipFile(tmp.name, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(annotated_path, arcname=f"{stem}_annotated.png")
        archive.write(csv_path, arcname=f"{stem}_detections.csv")
        archive.write(json_path, arcname=f"{stem}_results.json")

    for path in (annotated_path, csv_path, json_path):
        Path(path).unlink(missing_ok=True)

    return tmp.name


def export_batch_annotated_zip(
    annotated_paths: list[tuple[str, str]],
    max_images: int = 50,
) -> str:
    """
    Bundle annotated PNGs into a ZIP (limited to ``max_images`` for download size).
    """
    tmp = tempfile.NamedTemporaryFile(
        suffix=".zip",
        prefix="biodex_batch_annotated_",
        delete=False,
    )
    tmp.close()

    with zipfile.ZipFile(tmp.name, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for filename, path in annotated_paths[:max_images]:
            stem = Path(filename).stem or "image"
            archive.write(path, arcname=f"{stem}_annotated.png")

    return tmp.name


__all__ = [
    "CSV_COLUMNS",
    "batch_to_csv",
    "detections_to_csv",
    "export_batch_annotated_zip",
    "export_batch_json",
    "export_bundle",
    "export_json",
    "save_annotated_image",
]
