"""
Professional bounding-box visualization for BioDex v0.2.
"""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

from core.types import DetectionRecord, bbox_area, bbox_to_pixels

# User-specified conservation palette.
CATEGORY_COLORS: dict[str, str] = {
    "animal": "#2E7D32",
    "person": "#F57C00",
    "vehicle": "#C62828",
}
DEFAULT_COLOR = "#546E7A"

BOX_OUTLINE_WIDTH = 3
BOX_FILL_ALPHA = 48
LABEL_PADDING = 6
LABEL_GAP = 4


@dataclass
class _LabelPlacement:
    x0: int
    y0: int
    x1: int
    y1: int


def _load_font(size: int = 14) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a readable TrueType font when available, else fall back to default."""
    candidates = [
        "arial.ttf",
        "Arial.ttf",
        "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _hex_to_rgba(hex_color: str, alpha: int) -> tuple[int, int, int, int]:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return r, g, b, alpha


def _color_for_category(category: str) -> str:
    return CATEGORY_COLORS.get(category, DEFAULT_COLOR)


def _format_confidence(value: float) -> str:
    return f"{value * 100:.0f}%"


def _label_lines(detection: DetectionRecord) -> list[str]:
    category_line = f"{detection.category.title()} {_format_confidence(detection.confidence)}"
    if detection.species and detection.species.label:
        species_line = (
            f"{detection.species.label} "
            f"{_format_confidence(detection.species.confidence)}"
        )
        return [category_line, species_line]
    return [category_line]


def _measure_label_block(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    font: ImageFont.ImageFont,
) -> tuple[int, int]:
    max_width = 0
    total_height = 0
    for index, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]
        max_width = max(max_width, line_w)
        total_height += line_h
        if index < len(lines) - 1:
            total_height += LABEL_GAP
    return max_width + LABEL_PADDING * 2, total_height + LABEL_PADDING * 2


def _rects_overlap(a: _LabelPlacement, b: _LabelPlacement) -> bool:
    return not (a.x1 <= b.x0 or a.x0 >= b.x1 or a.y1 <= b.y0 or a.y0 >= b.y1)


def _find_label_position(
    *,
    box_x0: int,
    box_y0: int,
    box_x1: int,
    box_y1: int,
    label_w: int,
    label_h: int,
    image_w: int,
    image_h: int,
    occupied: list[_LabelPlacement],
) -> _LabelPlacement:
    """Place label above the box when possible; stack below or inside on collision."""
    candidates = [
        (box_x0, box_y0 - label_h),
        (box_x0, box_y1 + 2),
        (box_x0, min(box_y1 - label_h, image_h - label_h)),
        (box_x1 - label_w, box_y0 - label_h),
    ]

    for x, y in candidates:
        x = max(0, min(x, image_w - label_w))
        y = max(0, min(y, image_h - label_h))
        placement = _LabelPlacement(x, y, x + label_w, y + label_h)
        if not any(_rects_overlap(placement, other) for other in occupied):
            return placement

    # Last resort: push downward from the top-left of the box.
    y = min(box_y0 + 2, image_h - label_h)
    x = max(0, min(box_x0, image_w - label_w))
    return _LabelPlacement(x, y, x + label_w, y + label_h)


def draw_detections(image: Image.Image, detections: list[DetectionRecord]) -> Image.Image:
    """
    Draw bounding boxes and labels on a copy of the input image.

    Large boxes are drawn first; labels avoid overlap via simple placement rules.
    """
    base = image.copy()
    if base.mode != "RGB":
        base = base.convert("RGB")

    if not detections:
        return base

    width, height = base.size
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    draw = ImageDraw.Draw(base)
    font = _load_font()

    sorted_detections = sorted(detections, key=lambda d: bbox_area(d.bbox), reverse=True)
    occupied_labels: list[_LabelPlacement] = []

    for detection in sorted_detections:
        if len(detection.bbox) != 4:
            continue

        color = _color_for_category(detection.category)
        fill_rgba = _hex_to_rgba(color, BOX_FILL_ALPHA)
        x0, y0, x1, y1 = bbox_to_pixels(detection.bbox, width, height)

        overlay_draw.rectangle([x0, y0, x1, y1], fill=fill_rgba, outline=None)
        draw.rectangle([x0, y0, x1, y1], outline=color, width=BOX_OUTLINE_WIDTH)

        lines = _label_lines(detection)
        label_w, label_h = _measure_label_block(draw, lines, font)
        placement = _find_label_position(
            box_x0=x0,
            box_y0=y0,
            box_x1=x1,
            box_y1=y1,
            label_w=label_w,
            label_h=label_h,
            image_w=width,
            image_h=height,
            occupied=occupied_labels,
        )
        occupied_labels.append(placement)

        draw.rectangle(
            [placement.x0, placement.y0, placement.x1, placement.y1],
            fill=color,
        )

        text_y = placement.y0 + LABEL_PADDING
        for line in lines:
            draw.text((placement.x0 + LABEL_PADDING, text_y), line, fill="white", font=font)
            line_bbox = draw.textbbox((0, 0), line, font=font)
            text_y += (line_bbox[3] - line_bbox[1]) + LABEL_GAP

    annotated = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    return annotated
