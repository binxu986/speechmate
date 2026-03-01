@echo off
REM SpeechMate Client Start Script for Windows

cd /d "%~dp0client"

echo Starting SpeechMate Client...

REM Check if venv exists
if not exist "venv" (
    echo Virtual environment not found. Run install.bat first.
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

REM Create data directory if needed
if not exist "data" mkdir data

REM Start the client
python app\main.py

call deactivate