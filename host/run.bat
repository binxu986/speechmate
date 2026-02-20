@echo off
cd /d "%~dp0"
set PYTHONPATH=.
echo ====================================
echo   SpeechMate API Server
echo ====================================
echo.
python -m src.api_server
pause
