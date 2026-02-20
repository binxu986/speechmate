@echo off
chcp 65001 >nul
echo ====================================
echo   SpeechMate Host Deployment
echo ====================================
echo.

cd /d "%~dp0"

echo [1/5] Creating Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo [2/5] Installing Python dependencies...
pip install -r requirements.txt

echo [3/5] Checking ffmpeg...
where ffmpeg >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ffmpeg not found, please install manually
    echo Run: choco install ffmpeg
)

echo [4/5] Downloading default model...
python -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu', compute_type='int8')"

echo.
echo ====================================
echo   Deployment Complete!
echo ====================================
echo Visit http://localhost:3456
echo Press Ctrl+C to stop
echo.

echo [5/5] Starting service...
python -m src.api_server

pause
