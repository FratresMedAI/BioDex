"""EXIF and GPS metadata helpers for camera-trap exports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from PIL import Image
from PIL.ExifTags import TAGS


@dataclass(frozen=True)
class ImageMetadata:
    """Extracted metadata from a camera-trap image."""

    latitude: float | None = None
    longitude: float | None = None
    timestamp: str | None = None
    camera_make: str | None = None
    camera_model: str | None = None


def _rational_to_float(value: Any) -> float | None:
    try:
        if hasattr(value, "numerator") and hasattr(value, "denominator"):
            if value.denominator == 0:
                return None
            return float(value.numerator) / float(value.denominator)
        return float(value)
    except (TypeError, ValueError):
        return None


def _dms_to_decimal(dms: tuple[Any, Any, Any], ref: str) -> float | None:
    try:
        degrees = _rational_to_float(dms[0])
        minutes = _rational_to_float(dms[1])
        seconds = _rational_to_float(dms[2])
        if degrees is None or minutes is None or seconds is None:
            return None
        decimal = degrees + minutes / 60.0 + seconds / 3600.0
        if ref in ("S", "W"):
            decimal = -decimal
        return decimal
    except (IndexError, TypeError):
        return None


def extract_metadata(image: Image.Image) -> ImageMetadata:
    """Read GPS and timestamp EXIF from a PIL image."""
    try:
        exif = image.getexif()
    except Exception:
        return ImageMetadata()

    if not exif:
        return ImageMetadata()

    tagged: dict[str, Any] = {}
    for tag_id, value in exif.items():
        name = TAGS.get(tag_id, str(tag_id))
        tagged[name] = value

    timestamp: str | None = None
    for key in ("DateTimeOriginal", "DateTime", "DateTimeDigitized"):
        raw = tagged.get(key)
        if raw:
            timestamp = str(raw)
            break

    latitude: float | None = None
    longitude: float | None = None
    gps_info = tagged.get("GPSInfo")
    if isinstance(gps_info, dict):
        gps: dict[int, Any] = gps_info
        lat = gps.get(2)
        lat_ref = gps.get(1, "N")
        lon = gps.get(4)
        lon_ref = gps.get(3, "E")
        if lat and lon:
            latitude = _dms_to_decimal(tuple(lat), str(lat_ref))
            longitude = _dms_to_decimal(tuple(lon), str(lon_ref))

    return ImageMetadata(
        latitude=latitude,
        longitude=longitude,
        timestamp=timestamp,
        camera_make=str(tagged.get("Make", "") or "") or None,
        camera_model=str(tagged.get("Model", "") or "") or None,
    )


def parse_exif_timestamp(raw: str | None) -> datetime | None:
    """Parse common EXIF datetime strings."""
    if not raw:
        return None
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(raw.strip(), fmt)
        except ValueError:
            continue
    return None


def metadata_to_export_fields(meta: ImageMetadata) -> dict[str, Any]:
    """Flatten metadata for CSV/JSON export rows."""
    return {
        "latitude": meta.latitude if meta.latitude is not None else "",
        "longitude": meta.longitude if meta.longitude is not None else "",
        "capture_timestamp": meta.timestamp or "",
        "camera_make": meta.camera_make or "",
        "camera_model": meta.camera_model or "",
    }


__all__ = [
    "ImageMetadata",
    "extract_metadata",
    "metadata_to_export_fields",
    "parse_exif_timestamp",
]
