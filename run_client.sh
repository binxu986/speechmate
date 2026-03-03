#!/bin/bash
# SpeechMate Client - Quick Start

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/client"

echo "Starting SpeechMate Client..."

if [ ! -d "venv" ]; then
    echo "[ERROR] venv not found. Run install.sh first."
    exit 1
fi

source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
python app/main.py
