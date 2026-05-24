"""BioDex core modules for detection, classification, visualization, and export."""

from core.classifier import enrich_with_species, get_classifier
from core.detector import (
    CATEGORY_MAP,
    MODEL_ID,
    get_category_label,
    get_detector,
    run_analysis,
    run_detection,
)
from core.exports import detections_to_csv, export_json, save_annotated_image
from core.types import (
    BIODEX_VERSION,
    AnalysisResult,
    DetectionRecord,
    SpeciesPrediction,
)
from core.visualization import draw_detections

__all__ = [
    "BIODEX_VERSION",
    "CATEGORY_MAP",
    "MODEL_ID",
    "AnalysisResult",
    "DetectionRecord",
    "SpeciesPrediction",
    "draw_detections",
    "detections_to_csv",
    "enrich_with_species",
    "export_json",
    "get_category_label",
    "get_classifier",
    "get_detector",
    "run_analysis",
    "run_detection",
    "save_annotated_image",
]
