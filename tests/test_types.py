"""Unit tests for core.types helpers."""

from core.types import (
    bbox_area,
    bbox_to_pixels,
    crop_from_bbox,
    format_species_alternatives,
    format_taxon_label,
    get_category_label,
    SpeciesPrediction,
)
from PIL import Image


def test_get_category_label():
    assert get_category_label("1") == "animal"
    assert get_category_label("2") == "person"
    assert get_category_label("99") == "unknown (99)"


def test_format_taxon_label():
    assert format_taxon_label("mammalia;macropus_giganteus") == "Macropus Giganteus"
    assert format_taxon_label("blank") == "Blank"
    assert format_taxon_label("") == "Unknown"


def test_format_species_alternatives():
    species = SpeciesPrediction(
        label="Deer",
        confidence=0.55,
        top3=[("Deer", 0.55), ("Elk", 0.20), ("Blank", 0.005)],
        confidence_tier="borderline",
    )
    text = format_species_alternatives(species)
    assert "Elk" in text
    assert "Ocelot" not in text


def test_bbox_to_pixels():
    x0, y0, x1, y1 = bbox_to_pixels([0.1, 0.2, 0.3, 0.4], 100, 200)
    assert (x0, y0, x1, y1) == (10, 40, 40, 120)


def test_bbox_area():
    assert bbox_area([0.5, 0.0, 0.2, 0.3]) == 0.06


def test_crop_from_bbox():
    image = Image.new("RGB", (100, 100), color=(255, 0, 0))
    crop = crop_from_bbox(image, [0.25, 0.25, 0.5, 0.5])
    assert crop.size[0] > 0 and crop.size[1] > 0
