@echo off
cd /d "%~dp0\.."

if not exist ".venv\Scripts\activate.bat" (
    echo Installing BioDex first...
    powershell -ExecutionPolicy Bypass -File scripts\install_biodex.ps1
)

call .venv\Scripts\activate.bat
set BIODEX_DEPLOY=1
cd demo
echo Limited demo -^> http://127.0.0.1:7860 ^(max 30 images, no ZIP^)
python app.py
