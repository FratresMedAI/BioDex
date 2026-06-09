"""Basic analytics for batch results (requires ``[analytics]`` extra)."""

from __future__ import annotations

import logging
import math
import tempfile
from pathlib import Path
from typing import Any

from core.exif_utils import extract_metadata, parse_exif_timestamp
from core.types import BatchResult

logger = logging.getLogger(__name__)


def _require_analytics() -> None:
    try:
        import matplotlib  # noqa: F401
        import seaborn  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "Analytics requires matplotlib and seaborn. Install with: pip install 'biodex[analytics]'"
        ) from exc


def compute_diversity_index(species_counts: dict[str, int]) -> dict[str, float]:
    """
    Compute Shannon and Simpson diversity indices from species frequency counts.

    Returns zeros when no species are present.
    """
    total = sum(species_counts.values())
    if total == 0:
        return {"shannon": 0.0, "simpson": 0.0, "richness": 0.0}

    proportions = [count / total for count in species_counts.values()]
    shannon = -sum(p * math.log(p) for p in proportions if p > 0)
    simpson = 1.0 - sum(p * p for p in proportions)
    return {
        "shannon": round(shannon, 4),
        "simpson": round(simpson, 4),
        "richness": float(len(species_counts)),
    }


def activity_heatmap(
    batch: BatchResult,
    images: list[tuple[str, Any]] | None = None,
    *,
    group_by: str = "hour",
) -> Path:
    """
    Generate a PNG activity heatmap from EXIF timestamps (fallback: index order).

    Returns path to a temporary PNG file.
    """
    _require_analytics()
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt
    import seaborn as sns

    image_by_name = {name: img for name, img in (images or [])}
    buckets: dict[int, int] = {}

    for index, result in enumerate(batch.results):
        dt = None
        source = image_by_name.get(result.filename)
        if source is not None:
            meta = extract_metadata(source)
            dt = parse_exif_timestamp(meta.timestamp)
        if dt is None:
            bucket_key = index % 24 if group_by == "hour" else index % 7
        elif group_by == "hour":
            bucket_key = dt.hour
        else:
            bucket_key = dt.weekday()
        buckets[bucket_key] = buckets.get(bucket_key, 0) + max(result.animal_count, 0)

    labels = list(range(24)) if group_by == "hour" else list(range(7))
    values = [buckets.get(label, 0) for label in labels]
    xlabel = "Hour of day" if group_by == "hour" else "Day of week (Mon=0)"

    fig, ax = plt.subplots(figsize=(9, 3.2), facecolor="#F5EDE3")
    ax.set_facecolor("#F5EDE3")
    sns.barplot(x=labels, y=values, ax=ax, color="#2d6a4f", edgecolor="#1b4332", linewidth=0.6)
    ax.set_xlabel(xlabel, color="#2C3328", fontsize=11, fontweight="bold")
    ax.set_ylabel("Animal detections", color="#2C3328", fontsize=11, fontweight="bold")
    ax.set_title("BioDex activity heatmap", color="#2C3328", fontsize=12, fontweight="bold", pad=10)
    ax.tick_params(axis="both", colors="#2C3328", labelsize=9)
    ax.grid(axis="y", color="#C9BFB0", linewidth=0.8, alpha=0.9)
    for spine in ax.spines.values():
        spine.set_color("#2C3328")
        spine.set_linewidth(1.0)
    fig.tight_layout()

    tmp = Path(tempfile.mkstemp(suffix=".png", prefix="biodex_heatmap_")[1])
    fig.savefig(tmp, dpi=140, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return tmp


def population_trend_stub(batch_results_over_time: list[BatchResult]) -> dict[str, Any]:
    """Structured placeholder for multi-session population trend analysis (v0.6+)."""
    totals = [b.animal_count for b in batch_results_over_time]
    return {
        "status": "stub",
        "sessions": len(batch_results_over_time),
        "animal_totals": totals,
        "message": "Population trend analysis requires multiple dated batch runs.",
    }


__all__ = ["activity_heatmap", "compute_diversity_index", "population_trend_stub"]
