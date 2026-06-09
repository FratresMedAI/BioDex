#!/usr/bin/env python3
"""Print the OIDC claims GitHub Actions sends for PyPI Trusted Publishing."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "publish.yml"


def main() -> None:
    if not WORKFLOW.is_file():
        raise SystemExit(f"Missing workflow: {WORKFLOW}")

    text = WORKFLOW.read_text(encoding="utf-8")
    env = "pypi"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("environment:"):
            env = stripped.split(":", 1)[1].strip()
            break

    print("PyPI Trusted Publisher must match these values exactly:")
    print()
    print("  Owner:              Fratres-X-Natura")
    print("  Repository name:      BioDex")
    print(f"  Workflow name:        {WORKFLOW.name}")
    print(f"  Environment name:     {env}")
    print()
    print("GitHub repo:          Fratres-X-Natura/BioDex")
    print("Actions variable:     PYPI_PUBLISH = true")
    print()
    print("Common mistakes:")
    print("  - Repository biodex     (actual repo is BioDex — case matters)")
    print("  - Workflow release.yml  (actual file is publish.yml)")
    print("  - Environment release   (actual environment is pypi)")


if __name__ == "__main__":
    main()
