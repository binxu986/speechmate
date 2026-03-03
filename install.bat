@echo off
REM SpeechMate Installation Script for Windows
REM One-click installation for development environment

setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ========================================
echo   SpeechMate Installation
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM Install Host
echo [1/3] Installing Host dependencies...
cd /d "%~dp0host"
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -q --upgrade pip
pip install -q -r requirements.txt
call deactivate
echo       Host dependencies installed!

REM Install Client
echo [2/3] Installing Client dependencies...
cd /d "%~dp0client"
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -q --upgrade pip
pip install -q -r requirements.txt
call deactivate
echo       Client dependencies installed!

REM Download ASR Model
echo [3/3] Downloading ASR model...
cd /d "%~dp0host"
call venv\Scripts\activate.bat
python download_model.py --model small
call deactivate

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Quick Start:
echo   Host:   run_host.bat
echo   Client: run_client.bat
echo   All:    start_all.bat
echo.
pause
