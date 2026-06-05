@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0.."

echo ==^> BioDex setup (Windows)

where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: python not found. Install Python 3.10-3.12.
  exit /b 1
)

python -m venv .venv
call .venv\Scripts\activate.bat

python -m pip install --upgrade pip wheel "setuptools>=65,<81"
pip install -r requirements.txt

python scripts\fetch_examples.py
python -c "from app import build_app; build_app(); print('app build OK')"

echo.
echo Setup complete. Next:
echo   .venv\Scripts\activate
echo   python scripts\smoke_test.py
echo   python app.py
