@echo off
chcp 65001 >nul
echo ====================================
echo   SpeechMate Host Deployment
echo ====================================
echo.

cd /d "%~dp0"

echo [1/4] Creating Python virtual environment...
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat

echo [2/4] Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo [3/4] Checking ffmpeg...
where ffmpeg >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing ffmpeg...
    choco install ffmpeg -y
)

echo.
echo ====================================
echo   Ready to Start!
echo ====================================
echo First run will download models automatically.
echo Visit http://localhost:3456 after starting
echo Press Ctrl+C to stop
echo.

echo [4/4] Starting service...
python -m src.api_server

pause
