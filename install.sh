#!/bin/bash
# SpeechMate Installation Script
# This script creates virtual environments and installs all dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  SpeechMate Installation Script${NC}"
echo -e "${GREEN}========================================${NC}"

# Function to log messages
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Install Host dependencies
install_host() {
    log "${YELLOW}Installing Host dependencies...${NC}"
    cd "$SCRIPT_DIR/host"

    if [ ! -d "venv" ]; then
        log "Creating virtual environment for host..."
        python -m venv venv
    fi

    # Activate venv
    source venv/Scripts/activate 2>/dev/null || source venv/bin/activate

    # Install dependencies
    log "Installing Python packages..."
    pip install -r requirements.txt

    deactivate
    log "${GREEN}Host dependencies installed!${NC}"
}

# Install Client dependencies
install_client() {
    log "${YELLOW}Installing Client dependencies...${NC}"
    cd "$SCRIPT_DIR/client"

    if [ ! -d "venv" ]; then
        log "Creating virtual environment for client..."
        python -m venv venv
    fi

    # Activate venv
    source venv/Scripts/activate 2>/dev/null || source venv/bin/activate

    # Install dependencies
    log "Installing Python packages..."
    pip install -r requirements.txt

    deactivate
    log "${GREEN}Client dependencies installed!${NC}"
}

# Download ASR models
download_models() {
    log "${YELLOW}Downloading ASR models (optional)...${NC}"
    cd "$SCRIPT_DIR/host"

    # Activate venv
    source venv/Scripts/activate 2>/dev/null || source venv/bin/activate

    # Download small model
    python -c "
import sys
sys.path.insert(0, '.')
from faster_whisper import WhisperModel
print('Downloading faster-whisper-small model...')
model = WhisperModel('small', device='cpu', compute_type='int8', download_root='./model_cache')
print('Model downloaded successfully')
" || log "${YELLOW}Model download skipped - will download on first use${NC}"

    deactivate
}

# Main
main() {
    log "Starting installation..."

    # Install host
    install_host

    # Install client
    install_client

    # Ask about model download
    read -p "Download ASR model now? (y/n, default: n): " download_choice
    if [ "$download_choice" = "y" ] || [ "$download_choice" = "Y" ]; then
        download_models
    fi

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Installation Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "To start the host server:  ./run_host.sh"
    echo "To start the client:       ./run_client.sh"
    echo ""
}

main "$@"