"""Unit tests for species classification helpers."""

from core.classifier import apply_species_confidence_tier, parse_species_result
from core.types import (
    DEFAULT_SPECIES_MIN_CONFIDENCE,
    SPECIES_TIER_BORDERLINE,
    SPECIES_TIER_HIGH,
    SPECIES_TIER_UNCERTAIN,
    UNCERTAIN_LABEL,
    SpeciesPrediction,
    format_species_alternatives,
    format_species_display,
    species_confidence_tier,
)


def test_species_confidence_tier() -> None:
    assert species_confidence_tier(0.85, DEFAULT_SPECIES_MIN_CONFIDENCE) == SPECIES_TIER_HIGH
    assert species_confidence_tier(0.55, DEFAULT_SPECIES_MIN_CONFIDENCE) == SPECIES_TIER_BORDERLINE
    assert species_confidence_tier(0.30, DEFAULT_SPECIES_MIN_CONFIDENCE) == SPECIES_TIER_UNCERTAIN


def test_parse_species_result_skips_blank_top() -> None:
    result = {
        "classifications": {
            "classes": ["blank", "mammalia;leopardus_pardalis"],
            "scores": [0.6, 0.55],
        }
    }
    prediction = parse_species_result(result)
    assert prediction is not None
    assert prediction.label == "Leopardus Pardalis"
    assert prediction.confidence == 0.55
    assert prediction.confidence_tier == SPECIES_TIER_BORDERLINE


def test_parse_species_result_all_blank_returns_none() -> None:
    result = {
        "classifications": {
            "classes": ["blank"],
            "scores": [0.99],
        }
    }
    assert parse_species_result(result) is None


def test_apply_species_confidence_tier_marks_low_as_uncertain() -> None:
    prediction = SpeciesPrediction(
        label="Deer",
        confidence=0.25,
        top3=[("Deer", 0.25)],
        confidence_tier=SPECIES_TIER_BORDERLINE,
    )
    filtered = apply_species_confidence_tier(prediction)
    assert filtered.label == UNCERTAIN_LABEL
    assert filtered.confidence_tier == SPECIES_TIER_UNCERTAIN


def test_format_species_alternatives_only_for_borderline() -> None:
    high = SpeciesPrediction(
        label="Ocelot",
        confidence=0.95,
        top3=[("Ocelot", 0.95), ("Felidae", 0.03)],
        confidence_tier=SPECIES_TIER_HIGH,
    )
    assert format_species_alternatives(high) == ""

    borderline = SpeciesPrediction(
        label="Deer",
        confidence=0.55,
        top3=[("Deer", 0.55), ("Elk", 0.20)],
        confidence_tier=SPECIES_TIER_BORDERLINE,
    )
    text = format_species_alternatives(borderline)
    assert "Elk" in text


def test_format_species_display_uncertain() -> None:
    uncertain = SpeciesPrediction(
        label=UNCERTAIN_LABEL,
        confidence=0.22,
        top3=[(UNCERTAIN_LABEL, 0.22), ("Deer", 0.18)],
        confidence_tier=SPECIES_TIER_UNCERTAIN,
    )
    text = format_species_display(uncertain)
    assert "Uncertain" in text
