# PyInstaller spec — BioDex desktop app (Windows .exe / macOS .app / Linux binary).
#
# Build (from repo root, after install_biodex.sh + pip install pyinstaller):
#   pyinstaller packaging/biodex-desktop.spec --noconfirm
#
# Output: dist/BioDex/BioDex(.exe)
# Ship the whole dist/BioDex folder, or wrap in Inno Setup / create-dmg.

from __future__ import annotations

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules

ROOT = Path(SPECPATH).parent

block_cipher = None

gradio_datas, gradio_binaries, gradio_hiddenimports = collect_all("gradio")
torch_datas, torch_binaries, torch_hiddenimports = collect_all("torch")
md_datas, md_binaries, md_hiddenimports = collect_all("megadetector")
sn_datas, sn_binaries, sn_hiddenimports = collect_all("speciesnet")

try:
    ort_datas, ort_binaries, ort_hiddenimports = collect_all("onnxruntime")
except Exception:
    ort_datas, ort_binaries, ort_hiddenimports = [], [], []

datas = (
    gradio_datas
    + torch_datas
    + md_datas
    + sn_datas
    + ort_datas
    + [
        (str(ROOT / "ui"), "ui"),
        (str(ROOT / "core"), "core"),
        (str(ROOT / "app.py"), "."),
        (str(ROOT / "examples" / "manifest.json"), "examples"),
    ]
)

binaries = gradio_binaries + torch_binaries + md_binaries + sn_binaries + ort_binaries

hiddenimports = (
    gradio_hiddenimports
    + torch_hiddenimports
    + md_hiddenimports
    + sn_hiddenimports
    + ort_hiddenimports
    + collect_submodules("core")
    + collect_submodules("ui")
    + collect_submodules("core.models")
    + [
        "app",
        "core.video",
        "core.analytics",
        "core.models",
        "core.models.megadetector",
        "core.models.speciesnet",
        "core.models.registry",
        "speciesnet",
        "PIL",
        "pandas",
        "numpy",
        "typer",
        "tqdm",
    ]
)

a = Analysis(
    [str(ROOT / "desktop" / "launcher.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "mypy", "ruff"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="BioDex",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="BioDex",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="BioDex.app",
        icon=None,
        bundle_identifier="com.fratresmedai.biodex",
        info_plist={
            "CFBundleDisplayName": "BioDex",
            "CFBundleName": "BioDex",
            "NSHighResolutionCapable": True,
        },
    )
