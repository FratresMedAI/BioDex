"""BioDex batch analysis CLI (Typer entry point)."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from PIL import Image

from core.batch import run_batch
from core.exports import (
    batch_to_csv,
    detections_to_csv,
    export_batch_json,
    export_json,
    save_annotated_image,
)
from core.visualization import draw_detections

logger = logging.getLogger(__name__)

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _collect_image_paths(input_dir: Path, recursive: bool) -> list[Path]:
    """Return sorted image paths under ``input_dir``."""
    if not input_dir.is_dir():
        raise ValueError(f"Input directory does not exist: {input_dir}")

    paths: list[Path] = []
    iterator = input_dir.rglob("*") if recursive else input_dir.iterdir()
    for path in iterator:
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
            paths.append(path)
    return sorted(paths)


def run_batch_cli(
    input_dir: Path,
    output_dir: Path,
    *,
    threshold: float = 0.25,
    classify_species: bool = False,
    recursive: bool = False,
    workers: int = 1,
    verbose: bool = False,
) -> int:
    """
    Analyze all images in ``input_dir`` and write per-image + summary artifacts.

    ``workers`` is reserved for future parallel execution; only sequential mode
    is implemented today.
    """
    _configure_logging(verbose)

    if workers != 1:
        logger.warning(
            "Parallel workers are not implemented yet; running sequentially (--workers=%s).",
            workers,
        )

    try:
        from tqdm import tqdm
    except ImportError as exc:
        raise RuntimeError(
            "tqdm is required for batch CLI progress. Install with: pip install tqdm"
        ) from exc

    image_paths = _collect_image_paths(input_dir, recursive)
    if not image_paths:
        logger.error("No JPG/PNG images found in %s", input_dir)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    per_image_dir = output_dir / "images"
    per_image_dir.mkdir(parents=True, exist_ok=True)

    pairs: list[tuple[str, Image.Image]] = []
    for path in image_paths:
        pairs.append((path.name, Image.open(path)))

    batch = run_batch(
        pairs,
        threshold=threshold,
        classify_species=classify_species,
        progress_callback=lambda cur, total, msg: logger.info("[%s/%s] %s", cur, total, msg),
    )

    for result in tqdm(batch.results, desc="Writing artifacts", unit="image"):
        stem = Path(result.filename).stem or "image"
        image_out = per_image_dir / stem
        image_out.mkdir(parents=True, exist_ok=True)

        if result.error:
            logger.warning("Skipping artifacts for failed image %s: %s", result.filename, result.error)
            continue

        source_path = next((p for p in image_paths if p.name == result.filename), None)
        if source_path is None:
            logger.warning("Could not locate source image for %s", result.filename)
            continue

        with Image.open(source_path) as img:
            annotated = draw_detections(img, result.detections)
            annotated_path = save_annotated_image(annotated, filename_prefix=f"{stem}_annotated_")
            csv_path = detections_to_csv(result)
            json_path = export_json(result)

        dest_annotated = image_out / f"{stem}_annotated.png"
        dest_csv = image_out / f"{stem}_detections.csv"
        dest_json = image_out / f"{stem}_results.json"
        Path(annotated_path).replace(dest_annotated)
        Path(csv_path).replace(dest_csv)
        Path(json_path).replace(dest_json)

    summary_csv = batch_to_csv(batch)
    summary_json = export_batch_json(batch)
    summary_csv_dest = output_dir / "batch_summary.csv"
    summary_json_dest = output_dir / "batch_summary.json"
    Path(summary_csv).replace(summary_csv_dest)
    Path(summary_json).replace(summary_json_dest)

    logger.info(
        "Batch complete: %s images, %s blanks, %s failures. Summary: %s",
        batch.total_images,
        batch.blank_count,
        len(batch.failed),
        summary_csv_dest,
    )
    return 0 if not batch.failed else 2


def main() -> None:
    """Console entry point for ``biodex`` script."""
    try:
        import typer
    except ImportError:
        import argparse

        parser = argparse.ArgumentParser(description="BioDex batch analysis")
        parser.add_argument("input_dir", type=Path)
        parser.add_argument("-o", "--output", type=Path, required=True)
        parser.add_argument("-t", "--threshold", type=float, default=0.25)
        parser.add_argument("--classify-species", action="store_true")
        parser.add_argument("-r", "--recursive", action="store_true")
        parser.add_argument("-w", "--workers", type=int, default=1)
        parser.add_argument("-v", "--verbose", action="store_true")
        args = parser.parse_args()
        sys.exit(
            run_batch_cli(
                args.input_dir,
                args.output,
                threshold=args.threshold,
                classify_species=args.classify_species,
                recursive=args.recursive,
                workers=args.workers,
                verbose=args.verbose,
            )
        )

    app = typer.Typer(help="BioDex batch camera-trap analysis")

    @app.command("analyze")
    def analyze(
        input_dir: Path = typer.Argument(..., help="Folder of camera trap images"),
        output_dir: Path = typer.Option(..., "--output", "-o", help="Output directory"),
        threshold: float = typer.Option(0.25, "--threshold", "-t"),
        classify_species: bool = typer.Option(False, "--classify-species"),
        recursive: bool = typer.Option(False, "--recursive", "-r"),
        workers: int = typer.Option(1, "--workers", "-w"),
        verbose: bool = typer.Option(False, "--verbose", "-v"),
    ) -> None:
        """Analyze a folder of images and write CSV/JSON/annotated outputs."""
        code = run_batch_cli(
            input_dir,
            output_dir,
            threshold=threshold,
            classify_species=classify_species,
            recursive=recursive,
            workers=workers,
            verbose=verbose,
        )
        raise typer.Exit(code=code)

    app()


__all__ = ["main", "run_batch_cli"]
