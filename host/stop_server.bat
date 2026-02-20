@echo off
chcp 65001 >nul
echo ====================================
echo   Stopping SpeechMate Service
echo ====================================
echo.

echo Finding and stopping processes...

:: Kill Python processes
taskkill /F /FI "WINDOWTITLE eq SpeechMate*" 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq uvicorn*" 2>nul

:: Kill by port 3456
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3456 ^| findstr LISTENING') do (
    echo Stopping process %%a
    taskkill /F /PID %%a 2>nul
)

echo.
echo ====================================
echo   All services stopped
echo ====================================
pause
