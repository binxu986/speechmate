@echo off
REM SpeechMate - Start All Services (Host + Client)

cd /d "%~dp0"

echo.
echo ========================================
echo   SpeechMate - Starting All Services
echo ========================================
echo.

REM Start Host in background
echo [1/2] Starting Host Server...
cd /d "%~dp0host"
if not exist "venv" (
    echo [ERROR] Host venv not found. Run install.bat first.
    pause
    exit /b 1
)
start "SpeechMate Host" cmd /c "venv\Scripts\activate.bat && python start_server.py"

REM Wait for host to start
echo       Waiting for host to initialize...
timeout /t 5 /nobreak >nul

REM Start Client
echo [2/2] Starting Client...
cd /d "%~dp0client"
if not exist "venv" (
    echo [ERROR] Client venv not found. Run install.bat first.
    pause
    exit /b 1
)
start "SpeechMate Client" cmd /c "venv\Scripts\activate.bat && python app\main.py"

echo.
echo ========================================
echo   All Services Started!
echo ========================================
echo.
echo Host Server:  http://localhost:8000
echo Web Admin:    http://localhost:5000
echo.
echo Close this window or press Ctrl+C to stop.
echo.

REM Keep window open and monitor
:loop
timeout /t 30 /nobreak >nul
goto loop
