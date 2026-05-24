"""
Bounding-box visualization for BioDex detection results.
"""

from __future__ import annotations

from typing import Any

from PIL import Image, ImageDraw, ImageFont

from core.detector import CATEGORY_MAP, get_category_label

# Conservation-friendly colors per detection class.
CATEGORY_COLORS: dict[str, str] = {
    "animal": "#2E7D32",
    "person": "#1565C0",
    "vehicle": "#E65100",
}
DEFAULT_COLOR = "#546E7A"

BOX_WIDTH = 3
LABEL_PADDING = 4


def _bbox_to_pixels(
    bbox: list[float], width: int, height: int
) -> tuple[int, int, int, int]:
    """
    Convert MegaDetector normalized bbox [xmin, ymin, w, h] to pixel coords.

    Returns (x0, y0, x1, y1) clamped to image bounds.
    """
    xmin, ymin, box_w, box_h = bbox
    x0 = int(xmin * width)
    y0 = int(ymin * height)
    x1 = int((xmin + box_w) * width)
    y1 = int((ymin + box_h) * height)

    x0 = max(0, min(x0, width - 1))
    y0 = max(0, min(y0, height - 1))
    x1 = max(0, min(x1, width))
    y1 = max(0, min(y1, height))
    return x0, y0, x1, y1


def _color_for_category(category_id: str) -> str:
    label = get_category_label(category_id)
    return CATEGORY_COLORS.get(label, DEFAULT_COLOR)


def draw_detections(
    image: Image.Image,
    detections: list[dict[str, Any]],
    category_map: dict[str, str] | None = None,
) -> Image.Image:
    """
    Draw bounding boxes and labels on a copy of the input image.

    Args:
        image: Original PIL image.
        detections: Filtered MegaDetector detection dicts.
        category_map: Optional override for category ID → label mapping.

    Returns:
        New PIL image with annotations drawn.
    """
    _ = category_map or CATEGORY_MAP  # reserved for future custom maps
    annotated = image.copy()
    if annotated.mode != "RGB":
        annotated = annotated.convert("RGB")

    draw = ImageDraw.Draw(annotated)
    font = ImageFont.load_default()
    width, height = annotated.size

    for detection in detections:
        bbox = detection.get("bbox")
        if not bbox or len(bbox) != 4:
            continue

        category_id = str(detection.get("category", ""))
        conf = float(detection.get("conf", 0.0))
        label_name = get_category_label(category_id).title()
        label_text = f"{label_name} {conf:.2f}"
        color = _color_for_category(category_id)

        x0, y0, x1, y1 = _bbox_to_pixels(bbox, width, height)
        draw.rectangle([x0, y0, x1, y1], outline=color, width=BOX_WIDTH)

        # Label background for readability on varied camera-trap backgrounds.
        text_bbox = draw.textbbox((x0, y0), label_text, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        label_y = max(0, y0 - text_h - LABEL_PADDING * 2)
        draw.rectangle(
            [x0, label_y, x0 + text_w + LABEL_PADDING * 2, label_y + text_h + LABEL_PADDING * 2],
            fill=color,
        )
        draw.text(
            (x0 + LABEL_PADDING, label_y + LABEL_PADDING),
            label_text,
            fill="white",
            font=font,
        )

    return annotated
