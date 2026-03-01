@echo off
REM SpeechMate Host Server Start Script for Windows

cd /d "%~dp0host"

echo Starting SpeechMate Host Server...

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
if not exist "logs" mkdir logs
if not exist "model_cache" mkdir model_cache

REM Start the server
python start_server.py %*

call deactivate