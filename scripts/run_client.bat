@echo off
REM SpeechMate Client - Quick Start

cd /d "%~dp0..\client"

echo Starting SpeechMate Client...

if not exist "venv" (
    echo [ERROR] venv not found. Run install.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python app\main.py
