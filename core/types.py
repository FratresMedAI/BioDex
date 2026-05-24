"""
Shared data types and geometry helpers for BioDex v0.2.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from PIL import Image

BIODEX_VERSION = "0.2"

# MegaDetector category IDs.
ANIMAL_CATEGORY_ID = "1"
PERSON_CATEGORY_ID = "2"
VEHICLE_CATEGORY_ID = "3"

CATEGORY_MAP: dict[str, str] = {
    ANIMAL_CATEGORY_ID: "animal",
    PERSON_CATEGORY_ID: "person",
    VEHICLE_CATEGORY_ID: "vehicle",
}


@dataclass
class SpeciesPrediction:
    """Top species classification for an animal detection crop."""

    label: str
    confidence: float
    top3: list[tuple[str, float]] = field(default_factory=list)


@dataclass
class DetectionRecord:
    """A single MegaDetector detection, optionally enriched with species."""

    detection_id: int
    category_id: str
    category: str
    confidence: float
    bbox: list[float]  # normalized [xmin, ymin, width, height]
    species: SpeciesPrediction | None = None


@dataclass
class AnalysisResult:
    """Full analysis output for one camera trap image."""

    detections: list[DetectionRecord]
    total: int
    animal_count: int
    person_count: int
    vehicle_count: int
    is_blank: bool
    threshold: float
    species_enabled: bool
    filename: str
    summary: str
    species_warning: str = ""


def get_category_label(category_id: str) -> str:
    """Map MegaDetector category ID to a readable label."""
    return CATEGORY_MAP.get(str(category_id), f"unknown ({category_id})")


def format_taxon_label(raw_label: str) -> str:
    """
    Convert SpeciesNet taxon strings to readable labels.

    Examples:
        "mammalia;macropus_giganteus" -> "Macropus giganteus"
        "blank" -> "Blank"
    """
    if not raw_label:
        return "Unknown"

    # SpeciesNet often uses semicolon-separated hierarchy; prefer the most specific part.
    parts = [part.strip() for part in raw_label.split(";") if part.strip()]
    label = parts[-1] if parts else raw_label
    label = label.replace("_", " ").strip()

    if label.lower() == "blank":
        return "Blank"

    return label.title()


def bbox_to_pixels(
    bbox: list[float], width: int, height: int
) -> tuple[int, int, int, int]:
    """
    Convert normalized bbox [xmin, ymin, w, h] to pixel coords (x0, y0, x1, y1).
    """
    xmin, ymin, box_w, box_h = bbox
    x0 = int(xmin * width)
    y0 = int(ymin * height)
    x1 = int((xmin + box_w) * width)
    y1 = int((ymin + box_h) * height)

    x0 = max(0, min(x0, width - 1))
    y0 = max(0, min(y0, height - 1))
    x1 = max(x0 + 1, min(x1, width))
    y1 = max(y0 + 1, min(y1, height))
    return x0, y0, x1, y1


def bbox_area(bbox: list[float]) -> float:
    """Return normalized bbox area for overlap sorting."""
    return max(0.0, bbox[2]) * max(0.0, bbox[3])


def crop_from_bbox(
    image: Image.Image,
    bbox: list[float],
    padding_ratio: float = 0.02,
) -> Image.Image:
    """
    Crop a region from a PIL image using a normalized MegaDetector bbox.

    Adds a small padding ratio and clamps to image bounds.
    """
    if image.mode != "RGB":
        image = image.convert("RGB")

    width, height = image.size
    xmin, ymin, box_w, box_h = bbox

    pad_x = box_w * padding_ratio
    pad_y = box_h * padding_ratio
    xmin = max(0.0, xmin - pad_x)
    ymin = max(0.0, ymin - pad_y)
    box_w = min(1.0 - xmin, box_w + 2 * pad_x)
    box_h = min(1.0 - ymin, box_h + 2 * pad_y)

    x0, y0, x1, y1 = bbox_to_pixels([xmin, ymin, box_w, box_h], width, height)
    return image.crop((x0, y0, x1, y1))
