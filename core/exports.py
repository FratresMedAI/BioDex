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


def _result_to_json_payload(
    result: AnalysisResult,
    *,
    human_review: bool = False,
    review_notes: str = "",
) -> dict[str, Any]:
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
        "human_review": human_review,
        "review_notes": review_notes,
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


def export_batch_json(
    batch: BatchResult,
    *,
    human_review: bool = False,
    review_notes: str = "",
) -> str:
    """Write batch analysis results to a temporary JSON file."""
    payload = {
        "biodex_version": BIODEX_VERSION,
        "total_images": batch.total_images,
        "processed_count": batch.processed_count,
        "failed_count": len(batch.failed),
        "interrupted": batch.interrupted,
        "threshold": batch.threshold,
        "species_enabled": batch.species_enabled,
        "human_review": human_review,
        "review_notes": review_notes,
        "summary": {
            "blank_count": batch.blank_count,
            "total_detections": batch.total_detections,
            "animals": batch.animal_count,
            "people": batch.person_count,
            "vehicles": batch.vehicle_count,
            "species_counts": batch.species_counts,
        },
        "failed": [{"filename": name, "error": err} for name, err in batch.failed],
        "results": [
            _result_to_json_payload(r, human_review=human_review, review_notes=review_notes)
            for r in batch.results
        ],
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


def build_batch_annotated_zip(
    batch: BatchResult,
    images: list[tuple[str, Image.Image]],
    max_images: int = 50,
) -> str | None:
    """
    Draw annotations for successful batch results and bundle them into a ZIP.

    Temporary annotated PNGs are removed after the archive is written.
    """
    from core.visualization import draw_detections

    image_by_name = {name: img for name, img in images}
    annotated_paths: list[tuple[str, str]] = []
    for result in batch.results:
        if result.error:
            continue
        source = image_by_name.get(result.filename)
        if source is None:
            continue
        annotated = draw_detections(source, result.detections)
        annotated_file = save_annotated_image(
            annotated,
            filename_prefix=f"biodex_{Path(result.filename).stem}_",
        )
        annotated_paths.append((result.filename, annotated_file))

    if not annotated_paths:
        return None

    zip_path = export_batch_annotated_zip(annotated_paths, max_images=max_images)
    for _, annotated_file in annotated_paths:
        Path(annotated_file).unlink(missing_ok=True)
    return zip_path


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


def export_wildlife_insights(batch: BatchResult, deployment_id: str = "biodex-local") -> str:
    """Write Wildlife Insights-compatible CSV."""
    rows: list[dict[str, Any]] = []
    for result in batch.results:
        exif_ts = result.timestamp or result.analyzed_at
        if result.detections:
            for detection in result.detections:
                xmin, ymin, width, height = detection.bbox
                rows.append(
                    {
                        "deploymentID": deployment_id,
                        "filename": result.filename,
                        "species": detection.species.label if detection.species else "",
                        "confidence": detection.confidence,
                        "bbox_x": xmin,
                        "bbox_y": ymin,
                        "bbox_w": width,
                        "bbox_h": height,
                        "timestamp": exif_ts,
                        "category": detection.category,
                    }
                )
        else:
            rows.append(
                {
                    "deploymentID": deployment_id,
                    "filename": result.filename,
                    "species": "",
                    "confidence": "",
                    "bbox_x": "",
                    "bbox_y": "",
                    "bbox_w": "",
                    "bbox_h": "",
                    "timestamp": exif_ts,
                    "category": "blank" if result.is_blank else "",
                }
            )

    df = pd.DataFrame(rows)
    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv",
        prefix="biodex_wi_",
        delete=False,
        newline="",
    )
    df.to_csv(tmp.name, index=False)
    tmp.close()
    return tmp.name


def export_inaturalist(batch: BatchResult) -> str:
    """Write iNaturalist observation draft CSV (manual review required)."""
    header = (
        "# BioDex iNaturalist export - MANUAL REVIEW REQUIRED before upload\n"
        "# Verify species labels and location before submitting to iNaturalist\n"
    )
    rows: list[dict[str, Any]] = []
    for result in batch.results:
        for detection in result.detections:
            if detection.category_id != "1" or not detection.species:
                continue
            rows.append(
                {
                    "observation_date": result.timestamp or result.analyzed_at,
                    "taxon_name": detection.species.label,
                    "description": f"Camera trap detection (confidence {detection.confidence:.2f})",
                    "filename": result.filename,
                    "latitude": "",
                    "longitude": "",
                }
            )

    df = pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["observation_date", "taxon_name", "description", "filename", "latitude", "longitude"]
    )
    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv",
        prefix="biodex_inat_",
        delete=False,
        newline="",
    )
    tmp.write(header)
    df.to_csv(tmp, index=False)
    tmp.close()
    return tmp.name


def export_timelapse_md(batch: BatchResult) -> str:
    """Write MegaDetector native JSON array (timelapse-compatible)."""
    images_payload: list[dict[str, Any]] = []
    for result in batch.results:
        detections_md = []
        for detection in result.detections:
            detections_md.append(
                {
                    "category": detection.category_id,
                    "conf": detection.confidence,
                    "bbox": detection.bbox,
                }
            )
        images_payload.append({"file": result.filename, "detections": detections_md})

    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        prefix="biodex_timelapse_",
        delete=False,
        encoding="utf-8",
    )
    json.dump(images_payload, tmp, indent=2)
    tmp.close()
    return tmp.name


def export_sqlite(batch: BatchResult, db_path: Path | str) -> str:
    """Write batch results to SQLite with images, detections, and species tables."""
    import sqlite3

    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY,
                filename TEXT,
                analyzed_at TEXT,
                is_blank INTEGER,
                animal_count INTEGER,
                threshold REAL
            );
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY,
                image_id INTEGER,
                category TEXT,
                confidence REAL,
                xmin REAL, ymin REAL, width REAL, height REAL,
                FOREIGN KEY (image_id) REFERENCES images(id)
            );
            CREATE TABLE IF NOT EXISTS species (
                id INTEGER PRIMARY KEY,
                detection_id INTEGER,
                label TEXT,
                confidence REAL,
                tier TEXT,
                FOREIGN KEY (detection_id) REFERENCES detections(id)
            );
            """
        )
        for result in batch.results:
            cur = conn.execute(
                "INSERT INTO images (filename, analyzed_at, is_blank, animal_count, threshold) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    result.filename,
                    result.analyzed_at,
                    int(result.is_blank),
                    result.animal_count,
                    result.threshold,
                ),
            )
            image_id = cur.lastrowid
            for detection in result.detections:
                cur = conn.execute(
                    "INSERT INTO detections (image_id, category, confidence, xmin, ymin, width, height) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        image_id,
                        detection.category,
                        detection.confidence,
                        detection.bbox[0],
                        detection.bbox[1],
                        detection.bbox[2],
                        detection.bbox[3],
                    ),
                )
                det_id = cur.lastrowid
                if detection.species:
                    conn.execute(
                        "INSERT INTO species (detection_id, label, confidence, tier) VALUES (?, ?, ?, ?)",
                        (
                            det_id,
                            detection.species.label,
                            detection.species.confidence,
                            detection.species.confidence_tier,
                        ),
                    )
        conn.commit()
    finally:
        conn.close()
    return str(path)


def _top_species_label(result: AnalysisResult) -> str:
    best = ""
    best_conf = -1.0
    for detection in result.detections:
        if detection.species and detection.species.confidence > best_conf:
            best_conf = detection.species.confidence
            best = detection.species.label
    return best


def export_ecosentinel(batch: BatchResult) -> str:
    """Fratres EcoSentinel hook — versioned JSON schema stub for sensor fusion."""
    payload = {
        "schema_version": "ecosentinel/0.5-stub",
        "source": "biodex",
        "biodex_version": BIODEX_VERSION,
        "total_images": batch.total_images,
        "summary": {
            "animals": batch.animal_count,
            "species_counts": batch.species_counts,
        },
        "observations": [
            {
                "filename": r.filename,
                "timestamp": r.timestamp or r.analyzed_at,
                "detections": len(r.detections),
                "top_species": _top_species_label(r),
            }
            for r in batch.results
            if not r.error
        ],
        "fusion_ready": False,
        "note": "EcoSentinel integration stub — full drone/sensor fusion in Fratres stack",
    }
    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        prefix="biodex_ecosentinel_",
        delete=False,
        encoding="utf-8",
    )
    json.dump(payload, tmp, indent=2)
    tmp.close()
    return tmp.name


__all__ = [
    "CSV_COLUMNS",
    "batch_to_csv",
    "build_batch_annotated_zip",
    "detections_to_csv",
    "export_batch_annotated_zip",
    "export_batch_json",
    "export_bundle",
    "export_ecosentinel",
    "export_inaturalist",
    "export_json",
    "export_sqlite",
    "export_timelapse_md",
    "export_wildlife_insights",
    "save_annotated_image",
]
