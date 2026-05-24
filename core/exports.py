"""
Export helpers for BioDex detection results (CSV, JSON, and annotated images).
"""

from __future__ import annotations

import json
import tempfile
from typing import Any

import pandas as pd
from PIL import Image

from core.types import BIODEX_VERSION, AnalysisResult, DetectionRecord


def _format_top3(species) -> str:
    if not species or not species.top3:
        return ""
    return "|".join(f"{label}:{score:.4f}" for label, score in species.top3)


def _detection_to_row(result: AnalysisResult, detection: DetectionRecord) -> dict[str, Any]:
    bbox = detection.bbox
    species = detection.species
    return {
        "filename": result.filename,
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
        "species_top3": _format_top3(species),
        "threshold": result.threshold,
        "species_enabled": result.species_enabled,
    }


def detections_to_csv(result: AnalysisResult) -> str:
    """Write detections to a temporary CSV file and return its path."""
    rows = [_detection_to_row(result, detection) for detection in result.detections]

    df = pd.DataFrame(
        rows,
        columns=[
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
            "species_top3",
            "threshold",
            "species_enabled",
        ],
    )

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


def _detection_to_json_dict(detection: DetectionRecord) -> dict[str, Any]:
    species_payload = None
    if detection.species:
        species_payload = {
            "label": detection.species.label,
            "confidence": detection.species.confidence,
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


def export_json(result: AnalysisResult) -> str:
    """Write analysis results to a temporary JSON file and return its path."""
    payload = {
        "biodex_version": BIODEX_VERSION,
        "filename": result.filename,
        "threshold": result.threshold,
        "species_enabled": result.species_enabled,
        "is_blank": result.is_blank,
        "summary": result.summary,
        "counts": {
            "total": result.total,
            "animals": result.animal_count,
            "people": result.person_count,
            "vehicles": result.vehicle_count,
        },
        "detections": [_detection_to_json_dict(d) for d in result.detections],
    }

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


def save_annotated_image(image: Image.Image) -> str:
    """Save annotated image to a temporary PNG and return its path."""
    tmp = tempfile.NamedTemporaryFile(
        suffix=".png",
        prefix="biodex_annotated_",
        delete=False,
    )
    tmp.close()
    image.save(tmp.name, format="PNG")
    return tmp.name
