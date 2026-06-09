"""LLM-assisted review of camera-trap frames (BYOK).

Turns a BioDex ``AnalysisResult`` (+ optional image) into a field-style review
note: scene summary, a species second opinion that weighs in on SpeciesNet's
top guesses, and data-quality flags. Uses the user's saved BYOK provider.
"""

from __future__ import annotations

import base64
import io

from core.types import AnalysisResult, DetectionRecord
from PIL import Image

from ui.llm_settings import (
    DEFAULT_LOCAL_BASE_URL,
    DEFAULT_PROVIDER,
    generate,
    is_vision_capable,
    key_required,
)
from ui.settings_store import load_settings

SYSTEM_PROMPT = (
    "You are BioDex Field Assistant, an expert wildlife biologist helping a "
    "camera-trap reviewer triage detections. You are given a MegaDetector + "
    "SpeciesNet result for one frame, and (when available) the image itself.\n\n"
    "Write a concise markdown note with exactly these sections:\n"
    "### Summary\n"
    "One or two sentences on what the frame shows.\n"
    "### Species second opinion\n"
    "For each animal, say whether you agree with SpeciesNet's top label. If you "
    "disagree or it is uncertain, suggest the most likely species/genus and why "
    "(visible field marks, body shape, habitat). Be explicit about confidence.\n"
    "### Flags\n"
    "Bullet any data-quality issues: low detector/classifier confidence, likely "
    "false positives, motion blur, overexposure, partial/occluded animals, empty "
    "frame, or human/vehicle presence worth noting.\n\n"
    "Rules: Base species opinions on the image when provided; otherwise reason "
    "only from the metadata and say so. Never invent detections that are not "
    "listed. Keep it under ~180 words. Plain field language, no preamble."
)


def image_to_data_uri(image: Image.Image, *, max_side: int = 768, quality: int = 85) -> str:
    """Downscale to a JPEG data URI suitable for vision model inputs."""
    if image.mode != "RGB":
        image = image.convert("RGB")
    width, height = image.size
    longest = max(width, height)
    if longest > max_side:
        scale = max_side / float(longest)
        image = image.resize((max(1, int(width * scale)), max(1, int(height * scale))))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def _describe_detection(det: DetectionRecord) -> str:
    parts = [f"- {det.category} (detector confidence {det.confidence:.2f})"]
    if det.species:
        parts.append(f"SpeciesNet: {det.species.label} {det.species.confidence:.2f}")
        if det.species.confidence_tier:
            parts.append(f"tier={det.species.confidence_tier}")
        if det.species.top3:
            alts = ", ".join(f"{label} {score:.2f}" for label, score in det.species.top3[:3])
            parts.append(f"top-3: {alts}")
    return "; ".join(parts)


def build_frame_prompt(result: AnalysisResult) -> str:
    lines = [
        f"Filename: {result.filename}",
        f"Detection threshold: {result.threshold}",
        (
            f"Counts — animals: {result.animal_count}, people: {result.person_count}, "
            f"vehicles: {result.vehicle_count}, total: {result.total}"
        ),
        f"Species classification enabled: {result.species_enabled}",
    ]
    if result.is_blank:
        lines.append("Frame is BLANK (no detections above threshold).")
    if result.warnings:
        lines.append("Pipeline warnings: " + " | ".join(result.warnings))
    if result.detections:
        lines.append("Detections:")
        lines.extend(_describe_detection(det) for det in result.detections)
    return "\n".join(lines)


def review_frame(result: AnalysisResult, image: Image.Image | None) -> str:
    """Generate a markdown review note for one frame using saved BYOK settings."""
    settings = load_settings()
    provider = settings.get("llm_provider", DEFAULT_PROVIDER)
    api_key = settings.get("api_key", "")
    model = settings.get("llm_model", "")
    base_url = settings.get("llm_base_url", DEFAULT_LOCAL_BASE_URL)

    if key_required(provider) and not str(api_key).strip():
        return (
            "**No API key set.** Open **Use via API** in the footer, add your "
            "key, pick a model, then Save — and try again."
        )
    if not str(model).strip():
        return "**No model selected.** Open **Use via API** and choose a model."

    image_uri = None
    if image is not None and is_vision_capable(provider, model):
        image_uri = image_to_data_uri(image)

    user_prompt = build_frame_prompt(result)
    if image_uri is None and image is not None:
        user_prompt += (
            "\n\n(No image was sent — the selected model is text-only, so judge "
            "from the metadata above.)"
        )

    try:
        note = generate(
            provider,
            str(api_key),
            str(model),
            str(base_url),
            system=SYSTEM_PROMPT,
            user=user_prompt,
            image_uri=image_uri,
            max_tokens=700,
        )
    except Exception as exc:  # noqa: BLE001 — surface a friendly message in the UI
        return f"**AI review failed.** {exc}"

    note = note.strip()
    if not note:
        return "**AI review returned no text.** Try a different model."

    via = f"_via {provider} · {model}" + (" · vision_" if image_uri else " · text-only_")
    return f"{note}\n\n<sub>{via}</sub>"


__all__ = ["build_frame_prompt", "image_to_data_uri", "review_frame"]
