"""BioDex headless CLI — batch folder processing and video analysis."""

from __future__ import annotations

import logging
import os
import shutil
import sys
from pathlib import Path

from PIL import Image

from core.audit_log import append_audit_entry
from core.batch import run_batch_from_paths
from core.batch_report import format_batch_report
from core.config import get_model_settings
from core.exports import (
    batch_to_csv,
    build_batch_annotated_zip,
    detections_to_csv,
    export_batch_json,
    export_json,
    save_annotated_image,
)
from core.types import BatchResult
from core.video import analyze_video, export_video_timeline
from core.visualization import draw_detections

logger = logging.getLogger(__name__)

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        force=True,
    )


def _apply_torch_compile_env(enable: bool) -> None:
    if enable:
        os.environ["BIODEX_TORCH_COMPILE"] = "1"


def _collect_image_paths(input_dir: Path, recursive: bool) -> list[Path]:
    """Return sorted image paths under ``input_dir`` using stable relative names."""
    if not input_dir.is_dir():
        raise ValueError(f"Input directory does not exist: {input_dir}")

    paths: list[Path] = []
    iterator = input_dir.rglob("*") if recursive else input_dir.iterdir()
    for path in iterator:
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
            paths.append(path)
    return sorted(paths)


def _relative_name(path: Path, input_dir: Path) -> str:
    try:
        return path.relative_to(input_dir).as_posix()
    except ValueError:
        return path.name


def _write_batch_report(
    batch: BatchResult,
    *,
    input_dir: Path,
    output_dir: Path,
    summary_csv: Path,
    summary_json: Path,
    annotated_zip: Path | None,
) -> Path:
    report_path = output_dir / "batch_report.txt"
    report_path.write_text(
        format_batch_report(
            batch,
            input_dir=input_dir,
            output_dir=output_dir,
            summary_csv=summary_csv,
            summary_json=summary_json,
            annotated_zip=annotated_zip,
        ),
        encoding="utf-8",
    )
    return report_path


def run_batch_cli(
    input_dir: Path,
    output_dir: Path,
    *,
    threshold: float = 0.25,
    classify_species: bool = False,
    recursive: bool = True,
    workers: int = 1,
    chunk_size: int | None = None,
    torch_compile: bool = False,
    verbose: bool = False,
    zip_limit: int = 100,
) -> int:
    """
    Analyze all images in ``input_dir`` and write per-image + summary artifacts.

    Returns:
        0 when all images succeed, 1 on fatal error, 2 when some images fail.
    """
    _configure_logging(verbose)
    _apply_torch_compile_env(torch_compile)
    settings = get_model_settings()
    if torch_compile:
        logger.info("torch.compile enabled via CLI (ModelSettings.torch_compile=%s)", settings.torch_compile)

    try:
        from tqdm import tqdm
    except ImportError as exc:
        raise RuntimeError(
            "tqdm is required for batch CLI progress. Install with: pip install tqdm"
        ) from exc

    try:
        image_paths = _collect_image_paths(input_dir, recursive)
    except ValueError as exc:
        logger.error("%s", exc)
        return 1

    if not image_paths:
        logger.error("No supported images found in %s (jpg/jpeg/png/webp)", input_dir)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    per_image_dir = output_dir / "images"
    per_image_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Starting batch: %s images from %s (species=%s, threshold=%s, recursive=%s, workers=%s, chunk=%s)",
        len(image_paths),
        input_dir,
        classify_species,
        threshold,
        recursive,
        workers,
        chunk_size,
    )

    path_pairs = [(_relative_name(path, input_dir), str(path)) for path in image_paths]
    path_by_name = {name: Path(path) for name, path in path_pairs}

    progress = tqdm(total=len(path_pairs), desc="Analyzing", unit="image")

    def on_progress(current: int, total: int, message: str, fraction: float | None = None) -> None:
        progress.set_description(message[:60])
        progress.n = current
        progress.refresh()
        logger.debug("[%s/%s] %s (%.1f%%)", current, total, message, (fraction or 0) * 100)

    batch = run_batch_from_paths(
        path_pairs,
        threshold=threshold,
        classify_species=classify_species,
        progress_callback=on_progress,
        chunk_size=chunk_size,
        workers=workers,
    )
    progress.close()

    for result in tqdm(batch.results, desc="Writing artifacts", unit="image"):
        if result.error:
            logger.warning("Failed %s: %s", result.filename, result.error)
            continue

        source_path = path_by_name.get(result.filename)
        if source_path is None:
            logger.warning("Could not locate source image for %s", result.filename)
            continue

        stem = Path(result.filename).stem or "image"
        safe_stem = result.filename.replace("/", "__").replace("\\", "__")
        image_out = per_image_dir / safe_stem
        image_out.mkdir(parents=True, exist_ok=True)

        with Image.open(source_path) as img:
            annotated = draw_detections(img.convert("RGB"), result.detections)
            annotated_path = save_annotated_image(annotated, filename_prefix=f"{stem}_annotated_")
            csv_path = detections_to_csv(result)
            json_path = export_json(result)

        shutil.move(annotated_path, image_out / f"{stem}_annotated.png")
        shutil.move(csv_path, image_out / f"{stem}_detections.csv")
        shutil.move(json_path, image_out / f"{stem}_results.json")

    summary_csv_dest = output_dir / "batch_summary.csv"
    summary_json_dest = output_dir / "batch_summary.json"
    shutil.move(batch_to_csv(batch), summary_csv_dest)
    shutil.move(export_batch_json(batch), summary_json_dest)

    annotated_zip_dest: Path | None = None
    pairs_for_zip: list[tuple[str, Image.Image]] = []
    for name, path in path_pairs:
        with Image.open(path) as img:
            pairs_for_zip.append((name, img.convert("RGB")))
    temp_zip = build_batch_annotated_zip(batch, pairs_for_zip, max_images=zip_limit)
    if temp_zip:
        annotated_zip_dest = output_dir / "batch_annotated.zip"
        shutil.move(temp_zip, annotated_zip_dest)

    report_path = _write_batch_report(
        batch,
        input_dir=input_dir,
        output_dir=output_dir,
        summary_csv=summary_csv_dest,
        summary_json=summary_json_dest,
        annotated_zip=annotated_zip_dest,
    )

    append_audit_entry(
        "batch_complete",
        {
            "input_dir": str(input_dir),
            "output_dir": str(output_dir),
            "total_images": batch.total_images,
            "failed": len(batch.failed),
            "interrupted": batch.interrupted,
        },
    )

    print(report_path.read_text(encoding="utf-8"))

    if batch.interrupted:
        logger.warning("Batch interrupted after %s images.", batch.processed_count)
        return 2

    if batch.failed:
        logger.error(
            "Batch finished with %s failure(s). See %s for details.",
            len(batch.failed),
            report_path,
        )
        return 2

    logger.info("Batch complete: %s images written to %s", batch.total_images, output_dir)
    return 0


def run_video_cli(
    video_path: Path,
    output_dir: Path,
    *,
    threshold: float = 0.25,
    classify_species: bool = False,
    fps: float | None = None,
    max_frames: int = 300,
    verbose: bool = False,
) -> int:
    """Analyze a video clip and write timeline JSON."""
    _configure_logging(verbose)

    if not video_path.is_file():
        logger.error("Video file not found: %s", video_path)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        from tqdm import tqdm

        progress = tqdm(total=100, desc="Analyzing video")

        def on_progress(current: int, total: int, message: str, fraction: float | None = None) -> None:
            frac = fraction if fraction is not None else current / max(total, 1)
            progress.n = int(frac * 100)
            progress.set_description(message[:50])
            progress.refresh()

        result = analyze_video(
            video_path,
            fps=fps,
            max_frames=max_frames,
            threshold=threshold,
            classify_species=classify_species,
            progress_callback=on_progress,
        )
        progress.close()
        timeline = export_video_timeline(result, output_dir)
        append_audit_entry(
            "video_complete",
            {"source": str(video_path), "frames": result.total_frames, "interrupted": result.interrupted},
        )
        logger.info("Video analysis complete: %s frames → %s", result.total_frames, timeline)
        return 0
    except Exception as exc:
        logger.error("Video analysis failed: %s", exc)
        return 1


def main() -> None:
    """Console entry point for ``biodex``."""
    try:
        import typer
    except ImportError:
        _main_argparse()
        return

    app = typer.Typer(
        name="biodex",
        help="BioDex — local camera-trap detection and species classification",
        no_args_is_help=True,
    )

    @app.command("batch")
    def batch_command(
        input_dir: Path = typer.Argument(..., help="Folder of camera-trap images"),
        output_dir: Path = typer.Option(..., "--output", "-o", help="Output directory"),
        threshold: float = typer.Option(0.25, "--threshold", "-t"),
        classify_species: bool = typer.Option(
            False,
            "--classify-species/--no-classify-species",
            help="Run SpeciesNet on animal detections",
        ),
        recursive: bool = typer.Option(
            True,
            "--recursive/--no-recursive",
            "-r",
            help="Include images in subfolders",
        ),
        workers: int = typer.Option(1, "--workers", "-w", help="Parallel I/O workers (inference single-process)"),
        chunk_size: int | None = typer.Option(None, "--chunk-size", help="Process in chunks; unload models between"),
        torch_compile: bool = typer.Option(False, "--torch-compile", help="Enable torch.compile (opt-in)"),
        zip_limit: int = typer.Option(
            100,
            "--zip-limit",
            help="Max annotated PNGs in batch_annotated.zip",
        ),
        verbose: bool = typer.Option(False, "--verbose", "-v"),
    ) -> None:
        """Process a folder of images and write CSV/JSON/annotated outputs."""
        code = run_batch_cli(
            input_dir,
            output_dir,
            threshold=threshold,
            classify_species=classify_species,
            recursive=recursive,
            workers=workers,
            chunk_size=chunk_size,
            torch_compile=torch_compile,
            verbose=verbose,
            zip_limit=zip_limit,
        )
        raise typer.Exit(code=code)

    @app.command("video")
    def video_command(
        video_path: Path = typer.Argument(..., help="Camera-trap video clip"),
        output_dir: Path = typer.Option(..., "--output", "-o", help="Output directory"),
        threshold: float = typer.Option(0.25, "--threshold", "-t"),
        classify_species: bool = typer.Option(False, "--classify-species"),
        fps: float | None = typer.Option(None, "--fps", help="Sample rate (frames per second)"),
        max_frames: int = typer.Option(300, "--max-frames"),
        verbose: bool = typer.Option(False, "--verbose", "-v"),
    ) -> None:
        """Extract frames from a video and run detection."""
        code = run_video_cli(
            video_path,
            output_dir,
            threshold=threshold,
            classify_species=classify_species,
            fps=fps,
            max_frames=max_frames,
            verbose=verbose,
        )
        raise typer.Exit(code=code)

    @app.command("analyze", hidden=True)
    def analyze_command(
        input_dir: Path = typer.Argument(...),
        output_dir: Path = typer.Option(..., "--output", "-o"),
        threshold: float = typer.Option(0.25, "--threshold", "-t"),
        classify_species: bool = typer.Option(False, "--classify-species"),
        recursive: bool = typer.Option(False, "--recursive", "-r"),
        workers: int = typer.Option(1, "--workers", "-w"),
        verbose: bool = typer.Option(False, "--verbose", "-v"),
    ) -> None:
        """Deprecated alias for ``biodex batch``."""
        typer.echo("Note: `biodex analyze` is deprecated; use `biodex batch`.", err=True)
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


def _main_argparse() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioDex batch camera-trap analysis")
    sub = parser.add_subparsers(dest="command", required=True)

    batch_parser = sub.add_parser("batch", help="Process a folder of images")
    batch_parser.add_argument("input_dir", type=Path)
    batch_parser.add_argument("-o", "--output", type=Path, required=True)
    batch_parser.add_argument("-t", "--threshold", type=float, default=0.25)
    batch_parser.add_argument("--classify-species", action="store_true")
    batch_parser.add_argument(
        "--recursive",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    batch_parser.add_argument("-w", "--workers", type=int, default=1)
    batch_parser.add_argument("--chunk-size", type=int, default=None)
    batch_parser.add_argument("--torch-compile", action="store_true")
    batch_parser.add_argument("--zip-limit", type=int, default=100)
    batch_parser.add_argument("-v", "--verbose", action="store_true")

    video_parser = sub.add_parser("video", help="Analyze a video clip")
    video_parser.add_argument("video_path", type=Path)
    video_parser.add_argument("-o", "--output", type=Path, required=True)
    video_parser.add_argument("-t", "--threshold", type=float, default=0.25)
    video_parser.add_argument("--classify-species", action="store_true")
    video_parser.add_argument("--fps", type=float, default=None)
    video_parser.add_argument("--max-frames", type=int, default=300)
    video_parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()
    if args.command == "batch":
        sys.exit(
            run_batch_cli(
                args.input_dir,
                args.output,
                threshold=args.threshold,
                classify_species=args.classify_species,
                recursive=args.recursive,
                workers=args.workers,
                chunk_size=args.chunk_size,
                torch_compile=args.torch_compile,
                verbose=args.verbose,
                zip_limit=args.zip_limit,
            )
        )
    if args.command == "video":
        sys.exit(
            run_video_cli(
                args.video_path,
                args.output,
                threshold=args.threshold,
                classify_species=args.classify_species,
                fps=args.fps,
                max_frames=args.max_frames,
                verbose=args.verbose,
            )
        )
    parser.error(f"Unknown command: {args.command}")


__all__ = ["main", "run_batch_cli", "run_video_cli"]
