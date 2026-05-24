"""
Export helpers for BioDex detection results (CSV and annotated images).
"""

from __future__ import annotations

import tempfile
from typing import Any

import pandas as pd
from PIL import Image

from core.detector import get_category_label


def detections_to_csv(
    detections: list[dict[str, Any]],
    image_name: str = "upload",
    threshold: float = 0.25,
) -> str:
    """
    Write detections to a temporary CSV file and return its path.

    Columns: image, category, category_id, confidence, xmin, ymin, width, height, threshold.
    """
    rows: list[dict[str, Any]] = []
    for detection in detections:
        bbox = detection.get("bbox", [0.0, 0.0, 0.0, 0.0])
        category_id = str(detection.get("category", ""))
        rows.append(
            {
                "image": image_name,
                "category": get_category_label(category_id),
                "category_id": category_id,
                "confidence": round(float(detection.get("conf", 0.0)), 4),
                "xmin": bbox[0],
                "ymin": bbox[1],
                "width": bbox[2],
                "height": bbox[3],
                "threshold": threshold,
            }
        )

    df = pd.DataFrame(
        rows,
        columns=[
            "image",
            "category",
            "category_id",
            "confidence",
            "xmin",
            "ymin",
            "width",
            "height",
            "threshold",
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
