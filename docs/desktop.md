# BioDex desktop application (future work)

> **Status: work in progress — not ready for distribution.**
>
> Use BioDex locally today with `bash scripts/install_biodex.sh` and `biodex-ui`.
> See the main [README](../README.md).

---

## Planned direction

Ship BioDex as normal software: install once, double-click, browser opens — no terminal.

The desktop build would bundle Python, Gradio, MegaDetector, SpeciesNet, and PyTorch. Model weights (~500 MB) would download on first use to a user data folder, not into the installer.

The headless **`biodex batch` CLI** would remain available via pip/source install for power users.

---

## Existing scaffolding (do not use yet)

| Path | Contents |
|------|----------|
| `packaging/biodex-desktop.spec` | PyInstaller spec (unverified) |
| `desktop/launcher.py` | Frozen-bundle entry point |
| `scripts/build_desktop.ps1` | Windows build script |
| `scripts/build_desktop.sh` | macOS/Linux build script |

These files are incomplete and unsupported until explicitly released.

---

## When desktop ships (draft notes)

- Output: `dist/BioDex/BioDex.exe` (Windows) or `dist/BioDex.app` (macOS)
- First-run model download to `~/BioDex` or `%USERPROFILE%\BioDex`
- Debug builds: set `console=True` in the spec
- Packaging options: zip folder, Inno Setup (Windows), create-dmg (macOS)
