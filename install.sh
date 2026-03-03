#!/bin/bash
# SpeechMate Installation Script
# One-click installation for development environment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  SpeechMate Installation${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check Python
if ! command -v python &> /dev/null; then
    echo -e "${RED}[ERROR] Python not found. Please install Python 3.10+${NC}"
    exit 1
fi

# Install Host
echo -e "${BLUE}[1/3] Installing Host dependencies...${NC}"
cd "$SCRIPT_DIR/host"
if [ ! -d "venv" ]; then
    python -m venv venv
fi
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
deactivate
echo -e "      ${GREEN}Host dependencies installed!${NC}"

# Install Client
echo -e "${BLUE}[2/3] Installing Client dependencies...${NC}"
cd "$SCRIPT_DIR/client"
if [ ! -d "venv" ]; then
    python -m venv venv
fi
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
deactivate
echo -e "      ${GREEN}Client dependencies installed!${NC}"

# Download ASR Model
echo -e "${BLUE}[3/3] Downloading ASR model...${NC}"
cd "$SCRIPT_DIR/host"
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
python download_model.py --model small
deactivate

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Quick Start:"
echo -e "  Host:   ${YELLOW}./run_host.sh${NC}"
echo -e "  Client: ${YELLOW}./run_client.sh${NC}"
echo -e "  All:    ${YELLOW}./start_all.sh${NC}"
echo ""
