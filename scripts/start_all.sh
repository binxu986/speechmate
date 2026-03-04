#!/bin/bash
# SpeechMate - Start All Services (Host + Client)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "========================================"
echo "  SpeechMate - Starting All Services"
echo "========================================"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $HOST_PID 2>/dev/null
    kill $CLIENT_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start Host
echo "[1/2] Starting Host Server..."
cd "$SCRIPT_DIR/../host"
if [ ! -d "venv" ]; then
    echo "[ERROR] Host venv not found. Run install.sh first."
    exit 1
fi
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
python start_server.py &
HOST_PID=$!
deactivate 2>/dev/null || true

# Wait for host
echo "      Waiting for host to initialize..."
sleep 3

# Start Client
echo "[2/2] Starting Client..."
cd "$SCRIPT_DIR/../client"
if [ ! -d "venv" ]; then
    echo "[ERROR] Client venv not found. Run install.sh first."
    kill $HOST_PID
    exit 1
fi
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
python app/main.py &
CLIENT_PID=$!

echo ""
echo "========================================"
echo "  All Services Started!"
echo "========================================"
echo ""
echo "Host Server:  http://localhost:8000"
echo "Web Admin:    http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop all services."
echo ""

# Wait for processes
wait
