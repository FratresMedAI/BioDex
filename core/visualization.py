"""
Report-grade bounding-box visualization for BioDex v0.4.

Draws color-coded boxes with readable labels, overlap-aware placement,
corner brackets for tiny detections, and an optional category legend.
"""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

from core.types import (
    DetectionRecord,
    bbox_area,
    bbox_to_pixels,
    format_confidence_pct,
    format_species_display,
)

CATEGORY_COLORS: dict[str, str] = {
    "animal": "#2E7D32",
    "person": "#F57C00",
    "vehicle": "#C62828",
}
DEFAULT_COLOR = "#546E7A"

BOX_OUTLINE_WIDTH = 3
BOX_OUTLINE_WIDTH_TINY = 2
BOX_FILL_ALPHA = 48
LABEL_PADDING = 6
LABEL_GAP = 4
LABEL_BG_ALPHA = 210
TINY_BOX_AREA = 0.002
LEGEND_MARGIN = 10
LEGEND_WIDTH = 130
LEGEND_HEIGHT = 88
CONNECTOR_WIDTH = 1
TEXT_STROKE_WIDTH = 2
BRACKET_LENGTH = 14


@dataclass
class _LabelPlacement:
    x0: int
    y0: int
    x1: int
    y1: int
    anchor_x: int
    anchor_y: int


def _adaptive_font_size(width: int, height: int) -> int:
    """Scale label font size with image dimensions (12–22 px)."""
    reference = max(width, height)
    return max(12, min(22, reference // 80))


def _load_font(size: int = 14) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a readable TrueType font when available, else fall back to default."""
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "arial.ttf",
        "DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
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


def _label_lines(detection: DetectionRecord) -> list[str]:
    category_line = (
        f"{detection.category.title()} {format_confidence_pct(detection.confidence)}"
    )
    if detection.species:
        species_text = format_species_display(detection.species)
        if species_text:
            return [category_line, species_text]
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


def _legend_zone(image_w: int, image_h: int) -> _LabelPlacement:
    x0 = LEGEND_MARGIN
    y0 = image_h - LEGEND_HEIGHT - LEGEND_MARGIN
    return _LabelPlacement(x0, y0, x0 + LEGEND_WIDTH, y0 + LEGEND_HEIGHT, x0, y0)


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
    prefer_inside: bool,
    legend: _LabelPlacement,
) -> _LabelPlacement:
    """Place label with expanded candidates; avoid legend and other labels."""
    candidates: list[tuple[int, int, int, int]] = []

    if prefer_inside:
        candidates.append((box_x0 + 2, box_y0 + 2, box_x0, box_y0))
    else:
        candidates.extend(
            [
                (box_x0, box_y0 - label_h - 2, box_x0, box_y0),
                (box_x0, box_y1 + 2, box_x0, box_y1),
                (box_x1 - label_w, box_y0 - label_h - 2, box_x1, box_y0),
                (box_x1 - label_w, box_y1 + 2, box_x1, box_y1),
                (box_x0 - label_w - 2, box_y0, box_x0, box_y0),
                (box_x1 + 2, box_y0, box_x1, box_y0),
                (box_x0, min(box_y1 - label_h - 2, image_h - label_h), box_x0, box_y1),
            ]
        )

    for x, y, anchor_x, anchor_y in candidates:
        x = max(0, min(x, image_w - label_w))
        y = max(0, min(y, image_h - label_h))
        placement = _LabelPlacement(x, y, x + label_w, y + label_h, anchor_x, anchor_y)
        if _rects_overlap(placement, legend):
            continue
        if not any(_rects_overlap(placement, other) for other in occupied):
            return placement

    y = min(max(box_y0 + 2, 0), image_h - label_h)
    x = max(0, min(box_x0, image_w - label_w))
    return _LabelPlacement(x, y, x + label_w, y + label_h, box_x0, box_y0)


def _draw_bracket_box(
    draw: ImageDraw.ImageDraw,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    color: str,
    width: int,
) -> None:
    """Draw corner brackets for tiny detections."""
    length = min(BRACKET_LENGTH, max(4, (x1 - x0) // 3, (y1 - y0) // 3))
    segments = [
        [(x0, y0), (x0 + length, y0), (x0, y0), (x0, y0 + length)],
        [(x1, y0), (x1 - length, y0), (x1, y0), (x1, y0 + length)],
        [(x0, y1), (x0 + length, y1), (x0, y1), (x0, y1 - length)],
        [(x1, y1), (x1 - length, y1), (x1, y1), (x1, y1 - length)],
    ]
    for start, end_h, _, end_v in segments:
        draw.line([start, end_h], fill=color, width=width)
        draw.line([start, end_v], fill=color, width=width)


def _draw_stroked_text(
    draw: ImageDraw.ImageDraw,
    position: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: str = "white",
    stroke: str = "#1B1B1B",
) -> None:
    """Draw text with a dark stroke for readability on varied backgrounds."""
    x, y = position
    draw.text((x, y), text, font=font, fill=stroke)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        draw.text((x + dx, y + dy), text, font=font, fill=stroke)
    draw.text((x, y), text, font=font, fill=fill)


def _draw_connector(
    draw: ImageDraw.ImageDraw,
    placement: _LabelPlacement,
    color: str,
) -> None:
    """Draw a thin line from the label to its anchor on the bounding box."""
    label_cx = (placement.x0 + placement.x1) // 2
    label_cy = placement.y1 if placement.y0 < placement.anchor_y else placement.y0
    draw.line(
        [(label_cx, label_cy), (placement.anchor_x, placement.anchor_y)],
        fill=color,
        width=CONNECTOR_WIDTH,
    )


def _draw_legend(
    overlay: Image.Image,
    font: ImageFont.ImageFont,
    title_font: ImageFont.ImageFont,
    image_w: int,
    image_h: int,
) -> None:
    """Draw a compact category legend on an RGBA overlay layer."""
    draw = ImageDraw.Draw(overlay)
    legend = _legend_zone(image_w, image_h)
    draw.rectangle(
        [legend.x0, legend.y0, legend.x1, legend.y1],
        fill=(255, 255, 255, LABEL_BG_ALPHA),
        outline=(176, 190, 197, 255),
        width=1,
    )
    draw.text((legend.x0 + 8, legend.y0 + 6), "BioDex", fill="#1B5E20", font=title_font)

    entries = [
        ("Animal", CATEGORY_COLORS["animal"]),
        ("Person", CATEGORY_COLORS["person"]),
        ("Vehicle", CATEGORY_COLORS["vehicle"]),
    ]
    swatch = 10
    row_start = legend.y0 + 26
    for index, (label, color) in enumerate(entries):
        row_y = row_start + index * 18
        draw.rectangle(
            [legend.x0 + 8, row_y, legend.x0 + 8 + swatch, row_y + swatch],
            fill=_hex_to_rgba(color, 255),
            outline=_hex_to_rgba(color, 255),
        )
        draw.text((legend.x0 + 24, row_y - 1), label, fill="#37474F", font=font)


def draw_detections(
    image: Image.Image,
    detections: list[DetectionRecord],
    *,
    show_legend: bool = True,
) -> Image.Image:
    """
    Draw bounding boxes and labels on a copy of the input image.

    Returns a PIL RGB image suitable for reports and demos.
    """
    base = image.copy()
    if base.mode != "RGB":
        base = base.convert("RGB")

    if not detections:
        return base

    width, height = base.size
    font_size = _adaptive_font_size(width, height)
    font = _load_font(font_size)
    legend_font = _load_font(max(10, font_size - 3))
    title_font = _load_font(max(11, font_size - 2))

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    label_overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    label_draw = ImageDraw.Draw(label_overlay)
    box_draw = ImageDraw.Draw(base)

    legend_zone = _legend_zone(width, height)
    sorted_detections = sorted(detections, key=lambda d: bbox_area(d.bbox))
    occupied_labels: list[_LabelPlacement] = []

    for detection in sorted_detections:
        if len(detection.bbox) != 4:
            continue

        color = _color_for_category(detection.category)
        fill_rgba = _hex_to_rgba(color, BOX_FILL_ALPHA)
        x0, y0, x1, y1 = bbox_to_pixels(detection.bbox, width, height)
        is_tiny = bbox_area(detection.bbox) < TINY_BOX_AREA
        outline_width = BOX_OUTLINE_WIDTH_TINY if is_tiny else BOX_OUTLINE_WIDTH

        overlay_draw.rectangle([x0, y0, x1, y1], fill=fill_rgba, outline=None)
        if is_tiny:
            _draw_bracket_box(box_draw, x0, y0, x1, y1, color, outline_width)
        else:
            box_draw.rectangle([x0, y0, x1, y1], outline=color, width=outline_width)

        lines = _label_lines(detection)
        measure_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        label_w, label_h = _measure_label_block(measure_draw, lines, font)
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
            prefer_inside=is_tiny,
            legend=legend_zone,
        )
        occupied_labels.append(placement)

        label_attached = (
            placement.y1 <= y0 + 2
            or placement.y0 >= y1 - 2
            or (placement.x0 >= x0 and placement.x1 <= x1 and placement.y0 >= y0)
        )
        if not label_attached and not is_tiny:
            _draw_connector(box_draw, placement, color)

        label_draw.rectangle(
            [placement.x0, placement.y0, placement.x1, placement.y1],
            fill=_hex_to_rgba(color, LABEL_BG_ALPHA),
            outline=_hex_to_rgba(color, 255),
            width=1,
        )

        text_y = placement.y0 + LABEL_PADDING
        for line in lines:
            _draw_stroked_text(
                label_draw,
                (placement.x0 + LABEL_PADDING, text_y),
                line,
                font,
            )
            line_bbox = measure_draw.textbbox((0, 0), line, font=font)
            text_y += (line_bbox[3] - line_bbox[1]) + LABEL_GAP

    if show_legend:
        _draw_legend(label_overlay, legend_font, title_font, width, height)

    annotated = Image.alpha_composite(base.convert("RGBA"), overlay)
    annotated = Image.alpha_composite(annotated, label_overlay).convert("RGB")
    return annotated
