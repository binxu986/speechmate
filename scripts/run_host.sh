#!/bin/bash
# SpeechMate Host Server - Quick Start

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../host"

echo "Starting SpeechMate Host..."

if [ ! -d "venv" ]; then
    echo "[ERROR] venv not found. Run install.sh first."
    exit 1
fi

source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
python start_server.py "$@"
