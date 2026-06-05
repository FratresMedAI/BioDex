@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\biodex-ui.exe" (
    if not exist ".venv\Scripts\biodex-ui" (
        echo First run — installing ^(5-10 min^). Needs Python 3.10-3.12 and internet.
        powershell -ExecutionPolicy Bypass -File scripts\install_biodex.ps1
    )
)

call .venv\Scripts\activate.bat
echo.
echo BioDex -^> http://127.0.0.1:7860
echo Upload a camera-trap folder, then click Process Folder.
echo.
biodex-ui
