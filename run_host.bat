@echo off
REM SpeechMate Host Server - Quick Start

cd /d "%~dp0host"

echo Starting SpeechMate Host...

if not exist "venv" (
    echo [ERROR] venv not found. Run install.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python start_server.py %*
call deactivate
