@echo off
setlocal

REM Always run from the folder where this .bat is located
cd /d "%~dp0"

echo ===============================
echo Starting Streamlit Application
echo Working directory: %CD%
echo ===============================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python is not available in PATH.
  echo Please install Python 3.10+ and check "Add Python to PATH".
  pause
  exit /b 1
)

REM Create venv if missing
if not exist venv (
  echo Creating virtual environment...
  python -m venv venv
)

REM Activate venv
call venv\Scripts\activate

REM Install deps
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Run Streamlit (app.py is inside the app folder)
python -m streamlit run app\app.py

pause
endlocal
