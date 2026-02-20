@echo off
chcp 65001 >nul
echo ====================================
echo   SpeechMate Host Deployment
echo ====================================
echo.

cd /d "%~dp0"

echo [1/3] Creating Python virtual environment...
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat

echo [2/3] Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ====================================
echo   Ready to Start!
echo ====================================
echo First run will download models automatically.
echo Visit http://localhost:3456 after starting
echo Press Ctrl+C to stop
echo.

echo [3/3] Starting service...
python -m src.api_server

pause
