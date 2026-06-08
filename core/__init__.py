"""BioDex core modules for detection, classification, visualization, and export."""

import core.models  # noqa: F401 — register default detector/classifier adapters
from core.batch import run_batch
from core.classifier import DEFAULT_SPECIES_MIN_CONFIDENCE, enrich_with_species, get_classifier
from core.detector import (
    CATEGORY_MAP,
    MODEL_ID,
    analyze_single_image,
    get_category_label,
    get_detector,
    run_analysis,
    run_detection,
)
from core.exports import (
    batch_to_csv,
    detections_to_csv,
    export_batch_json,
    export_bundle,
    export_json,
    save_annotated_image,
)
from core.types import (
    BIODEX_VERSION,
    AnalysisResult,
    BatchResult,
    DetectionRecord,
    SpeciesPrediction,
)
from core.visualization import draw_detections

__all__ = [
    "BIODEX_VERSION",
    "CATEGORY_MAP",
    "MODEL_ID",
    "AnalysisResult",
    "BatchResult",
    "DetectionRecord",
    "SpeciesPrediction",
    "analyze_single_image",
    "batch_to_csv",
    "draw_detections",
    "detections_to_csv",
    "enrich_with_species",
    "export_batch_json",
    "export_bundle",
    "export_json",
    "get_category_label",
    "get_classifier",
    "get_detector",
    "run_analysis",
    "run_batch",
    "run_detection",
    "save_annotated_image",
]
