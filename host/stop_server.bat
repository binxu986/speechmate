@echo off
chcp 65001 >nul
echo ====================================
echo   停止 SpeechMate 服务
echo ====================================
echo.

echo 正在查找并终止相关进程...

:: Kill Python processes
taskkill /F /FI "WINDOWTITLE eq SpeechMate*" 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq uvicorn*" 2>nul

:: Kill by port 3456
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3456 ^| findstr LISTENING') do (
    echo 终止进程 %%a
    taskkill /F /PID %%a 2>nul
)

echo.
echo ====================================
echo   所有服务已停止
echo ====================================
pause
