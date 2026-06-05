"""Quick MegaDetector load check (local GPU smoke test / CI)."""

from __future__ import annotations

import traceback


def main() -> None:
    try:
        from megadetector.detection import run_detector

        model = run_detector.load_detector("MDV5A")
        print("OK", type(model))
    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    main()
