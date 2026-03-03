@echo off
REM SpeechMate - Stop All Services

echo Stopping SpeechMate services...

REM Kill Host processes on ports 8000 and 5000
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000.*LISTENING"') do (
    echo Stopping process on port 8000: %%a
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":5000.*LISTENING"') do (
    echo Stopping process on port 5000: %%a
    taskkill /f /pid %%a >nul 2>&1
)

REM Kill Client by window title (SpeechMate window)
taskkill /f /fi "WindowTitle eq SpeechMate*" 2>nul
if %errorlevel%==0 echo Stopped SpeechMate client

echo All services stopped.
