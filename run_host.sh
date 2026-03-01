#!/bin/bash
# SpeechMate Host Server Start Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/host"

echo -e "${GREEN}Starting SpeechMate Host Server...${NC}"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Run install.sh first.${NC}"
    exit 1
fi

# Activate venv
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate

# Create data directory if needed
mkdir -p data logs model_cache

# Start the server
python start_server.py "$@"