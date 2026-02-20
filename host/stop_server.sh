#!/bin/bash

echo "=== 停止 SpeechMate 服务 ==="

# Kill Python processes related to this project
pkill -f "python.*src.api_server" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true

# Kill by port
if command -v fuser &> /dev/null; then
    fuser -k 3456/tcp 2>/dev/null || true
fi

echo "=== 所有服务已停止 ==="
