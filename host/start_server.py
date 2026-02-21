#!/usr/bin/env python3
"""
SpeechMate Host Server - One-click Start Script
This script sets up the environment and starts all services.
"""
import os
import sys
import subprocess
import signal
import threading
import time
import platform
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent.absolute()
VENV_DIR = BASE_DIR / "venv"
LOGS_DIR = BASE_DIR / "logs"
PID_FILE = BASE_DIR / "data" / "server.pid"

# Process list for cleanup
processes = []


def log(message):
    """Print log message with timestamp"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def get_python_executable():
    """Get Python executable path in virtual environment"""
    if platform.system() == "Windows":
        return str(VENV_DIR / "Scripts" / "python.exe")
    else:
        return str(VENV_DIR / "bin" / "python")


def get_pip_executable():
    """Get pip executable path in virtual environment"""
    if platform.system() == "Windows":
        return str(VENV_DIR / "Scripts" / "pip.exe")
    else:
        return str(VENV_DIR / "bin" / "pip")


def create_virtual_environment():
    """Create Python virtual environment"""
    if VENV_DIR.exists():
        log("Virtual environment already exists")
        return

    log("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
    log("Virtual environment created")


def install_dependencies():
    """Install required dependencies"""
    log("Installing dependencies...")
    pip_exe = get_pip_executable()

    # Upgrade pip first
    subprocess.run([pip_exe, "install", "--upgrade", "pip"], check=True)

    # Install requirements
    requirements_file = BASE_DIR / "requirements.txt"
    subprocess.run([pip_exe, "install", "-r", str(requirements_file)], check=True)
    log("Dependencies installed")


def download_models():
    """Pre-download models (optional)"""
    log("Pre-downloading models (this may take a while)...")

    python_exe = get_python_executable()

    # Download a small model by default
    download_script = '''
import sys
sys.path.insert(0, ".")
from faster_whisper import WhisperModel
print("Downloading faster-whisper-small model...")
model = WhisperModel("small", device="cpu", compute_type="int8", download_root="./model_cache")
print("Model downloaded successfully")
'''

    try:
        subprocess.run(
            [python_exe, "-c", download_script],
            cwd=str(BASE_DIR),
            timeout=600  # 10 minutes timeout
        )
    except subprocess.TimeoutExpired:
        log("Model download timeout - will download on first use")
    except Exception as e:
        log(f"Model download skipped: {e}")


def start_api_server():
    """Start FastAPI server"""
    log("Starting API server...")
    python_exe = get_python_executable()

    proc = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.main:app",
         "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(BASE_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    processes.append(proc)
    log(f"API server started (PID: {proc.pid})")
    return proc


def start_web_server():
    """Start Flask web admin server"""
    log("Starting web admin server...")
    python_exe = get_python_executable()

    proc = subprocess.Popen(
        [python_exe, "-m", "web.app"],
        cwd=str(BASE_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    processes.append(proc)
    log(f"Web admin server started (PID: {proc.pid})")
    return proc


def save_pids():
    """Save process PIDs to file"""
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PID_FILE, "w") as f:
        for proc in processes:
            f.write(f"{proc.pid}\n")


def cleanup(signum=None, frame=None):
    """Cleanup function to stop all services"""
    log("\nShutting down services...")

    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=5)
            log(f"Process {proc.pid} terminated")
        except:
            try:
                proc.kill()
                log(f"Process {proc.pid} killed")
            except:
                pass

    # Remove PID file
    if PID_FILE.exists():
        PID_FILE.unlink()

    log("All services stopped")
    sys.exit(0)


def print_server_info():
    """Print server information"""
    import socket

    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    local_ip = get_local_ip()

    print("\n" + "=" * 60)
    print("  SpeechMate Host Server Started Successfully!")
    print("=" * 60)
    print(f"\n  API Server:    http://{local_ip}:8000")
    print(f"  API Docs:      http://{local_ip}:8000/docs")
    print(f"  Web Admin:     http://{local_ip}:5000")
    print("\n  Press Ctrl+C to stop all services")
    print("=" * 60 + "\n")


def main():
    """Main entry point"""
    log("SpeechMate Host Server - Starting...")

    # Create logs directory
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Setup virtual environment
    create_virtual_environment()
    install_dependencies()

    # Download models (optional, can be skipped)
    if "--skip-models" not in sys.argv:
        try:
            download_models()
        except Exception as e:
            log(f"Model download failed: {e}")
            log("Models will be downloaded on first use")

    # Register signal handlers
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    if platform.system() != "Windows":
        signal.signal(signal.SIGQUIT, cleanup)

    # Start services
    start_api_server()
    time.sleep(2)  # Wait for API server to start
    start_web_server()

    # Save PIDs
    save_pids()

    # Print server info
    print_server_info()

    # Wait for processes
    try:
        while True:
            # Check if processes are still running
            for proc in processes:
                if proc.poll() is not None:
                    log(f"Process {proc.pid} exited unexpectedly")
                    cleanup()
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
