@echo off
REM SpeechMate Installation Script for Windows
REM This script creates virtual environments and installs all dependencies

setlocal EnableDelayedExpansion

echo ========================================
echo   SpeechMate Installation Script
echo ========================================

REM Get script directory
cd /d "%~dp0"

REM Install Host dependencies
echo.
echo [Installing Host dependencies...]
cd /d "%~dp0host"

if not exist "venv" (
    echo Creating virtual environment for host...
    python -m venv venv
)

echo Activating host virtual environment...
call venv\Scripts\activate.bat

echo Installing Python packages...
pip install -r requirements.txt

call deactivate
echo [Host dependencies installed!]

REM Install Client dependencies
echo.
echo [Installing Client dependencies...]
cd /d "%~dp0client"

if not exist "venv" (
    echo Creating virtual environment for client...
    python -m venv venv
)

echo Activating client virtual environment...
call venv\Scripts\activate.bat

echo Installing Python packages...
pip install -r requirements.txt

call deactivate
echo [Client dependencies installed!]

REM Ask about model download
echo.
set /p DOWNLOAD_CHOICE="Download ASR model now? (y/n, default: n): "
if /i "%DOWNLOAD_CHOICE%"=="y" (
    echo Downloading ASR model...
    cd /d "%~dp0host"
    call venv\Scripts\activate.bat
    python -c "import sys; sys.path.insert(0, '.'); from faster_whisper import WhisperModel; print('Downloading faster-whisper-small model...'); model = WhisperModel('small', device='cpu', compute_type='int8', download_root='./model_cache'); print('Model downloaded successfully')" 2>nul || echo Model download skipped - will download on first use
    call deactivate
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo To start the host server:  run_host.bat
echo To start the client:       run_client.bat
echo.

pause