#!/bin/bash
# SpeechMate - Stop All Services

echo "Stopping SpeechMate services..."

# Kill Host processes on ports 8000 and 5000
pkill -f "start_server.py" 2>/dev/null || true
pkill -f "uvicorn.*8000" 2>/dev/null || true
pkill -f "flask.*5000" 2>/dev/null || true
pkill -f "web.app" 2>/dev/null || true

# Kill Client process
pkill -f "client.*main.py" 2>/dev/null || true
pkill -f "app/main.py" 2>/dev/null || true

# Also try lsof if available
if command -v lsof &> /dev/null; then
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:5000 | xargs kill -9 2>/dev/null || true
fi

echo "All services stopped."
