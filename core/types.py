"""
Shared data types and geometry helpers for BioDex v0.4.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from PIL import Image

BIODEX_VERSION = "0.4"
MODEL_ID = "MDV5A"

# MegaDetector category IDs.
ANIMAL_CATEGORY_ID = "1"
PERSON_CATEGORY_ID = "2"
VEHICLE_CATEGORY_ID = "3"

CATEGORY_MAP: dict[str, str] = {
    ANIMAL_CATEGORY_ID: "animal",
    PERSON_CATEGORY_ID: "person",
    VEHICLE_CATEGORY_ID: "vehicle",
}

# Species confidence tiers.
SPECIES_TIER_HIGH = "high"
SPECIES_TIER_BORDERLINE = "borderline"
SPECIES_TIER_LOW = "low"
SPECIES_TIER_UNCERTAIN = "uncertain"

SPECIES_HIGH_THRESHOLD = 0.70
SPECIES_BORDERLINE_THRESHOLD = 0.40
DEFAULT_SPECIES_MIN_CONFIDENCE = 0.40
UNCERTAIN_LABEL = "Uncertain"
SPECIES_CROP_PADDING = 0.15


def utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def species_confidence_tier(confidence: float, species_min_confidence: float) -> str:
    """Map a species confidence score to a presentation tier."""
    if confidence < species_min_confidence:
        return SPECIES_TIER_UNCERTAIN
    if confidence >= SPECIES_HIGH_THRESHOLD:
        return SPECIES_TIER_HIGH
    if confidence >= SPECIES_BORDERLINE_THRESHOLD:
        return SPECIES_TIER_BORDERLINE
    return SPECIES_TIER_LOW


def is_blank_taxon_label(label: str) -> bool:
    """Return True when a formatted taxon label represents a blank prediction."""
    return label.strip().lower() == "blank"


@dataclass
class SpeciesPrediction:
    """Top species classification for an animal detection crop."""

    label: str
    confidence: float
    top3: list[tuple[str, float]] = field(default_factory=list)
    raw_label: str = ""
    confidence_tier: str = SPECIES_TIER_HIGH


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
    image_width: int = 0
    image_height: int = 0
    analyzed_at: str = field(default_factory=utc_now_iso)
    warnings: list[str] = field(default_factory=list)
    species_warning: str = ""
    error: str = ""
    model_id: str = ""
    inference_ms: float | None = None
    timestamp: str | None = None


@dataclass
class BatchResult:
    """Aggregate output from analyzing multiple camera trap images."""

    results: list[AnalysisResult]
    failed: list[tuple[str, str]]
    total_images: int
    processed_count: int
    blank_count: int
    total_detections: int
    animal_count: int
    person_count: int
    vehicle_count: int
    species_counts: dict[str, int] = field(default_factory=dict)
    threshold: float = 0.25
    species_enabled: bool = False


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

    parts = [part.strip() for part in raw_label.split(";") if part.strip()]
    label = parts[-1] if parts else raw_label
    label = label.replace("_", " ").strip()

    if label.lower() == "blank":
        return "Blank"

    return label.title()


def format_confidence_pct(value: float) -> str:
    """Format a 0–1 confidence as a percentage string."""
    return f"{value * 100:.0f}%"


def format_species_alternatives(
    species: SpeciesPrediction | None,
    *,
    exclude_top: bool = True,
) -> str:
    """
    Format species alternatives for UI and export columns.

    Only shown when confidence is borderline or low/uncertain.
    """
    if not species or not species.top3:
        return ""

    if species.confidence_tier not in (
        SPECIES_TIER_BORDERLINE,
        SPECIES_TIER_LOW,
        SPECIES_TIER_UNCERTAIN,
    ):
        return ""

    items = species.top3[1:] if exclude_top else species.top3
    items = [(label, score) for label, score in items if not is_blank_taxon_label(label)]
    if not items:
        return ""

    return " | ".join(f"{label} ({score:.2f})" for label, score in items)


def format_species_display(species: SpeciesPrediction | None) -> str:
    """Format species for labels and summaries."""
    if not species:
        return ""

    pct = format_confidence_pct(species.confidence)
    if species.confidence_tier == SPECIES_TIER_UNCERTAIN:
        alt = format_species_alternatives(species)
        if alt:
            first_alt = alt.split(" | ")[0]
            return f"Uncertain — maybe {first_alt}"
        return f"Uncertain ({pct})"

    if species.label == UNCERTAIN_LABEL:
        return f"Uncertain ({pct})"

    return f"{species.label} ({pct})"


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
