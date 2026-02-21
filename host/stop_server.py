#!/usr/bin/env python3
"""
SpeechMate Host Server - Stop Script
This script stops all running services and cleans up.
"""
import os
import sys
import signal
import subprocess
import platform
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent.absolute()
PID_FILE = BASE_DIR / "data" / "server.pid"

# Ports used by services
PORTS = [8000, 5000]


def log(message):
    """Print log message with timestamp"""
    import time
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def read_pids():
    """Read saved PIDs from file"""
    if not PID_FILE.exists():
        return []

    with open(PID_FILE, "r") as f:
        pids = []
        for line in f:
            line = line.strip()
            if line:
                try:
                    pids.append(int(line))
                except ValueError:
                    pass
        return pids


def kill_process_by_pid(pid):
    """Kill process by PID"""
    try:
        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                         capture_output=True, check=False)
        else:
            os.kill(pid, signal.SIGTERM)
        log(f"Killed process {pid}")
        return True
    except ProcessLookupError:
        log(f"Process {pid} not found")
        return False
    except Exception as e:
        log(f"Failed to kill process {pid}: {e}")
        return False


def find_processes_on_port(port):
    """Find processes listening on a specific port"""
    processes = []

    try:
        if platform.system() == "Windows":
            # Windows: use netstat
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True
            )

            for line in result.stdout.split("\n"):
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            pid = int(parts[-1])
                            processes.append(pid)
                        except ValueError:
                            pass
        else:
            # Linux/Mac: use lsof
            result = subprocess.run(
                ["lsof", "-i", f":{port}", "-t"],
                capture_output=True,
                text=True
            )

            for line in result.stdout.strip().split("\n"):
                if line:
                    try:
                        pid = int(line)
                        processes.append(pid)
                    except ValueError:
                        pass
    except Exception as e:
        log(f"Error finding processes on port {port}: {e}")

    return processes


def kill_port_processes():
    """Kill all processes on service ports"""
    log("Checking for processes on service ports...")

    for port in PORTS:
        pids = find_processes_on_port(port)
        for pid in pids:
            kill_process_by_pid(pid)


def stop_by_pid_file():
    """Stop services using saved PIDs"""
    pids = read_pids()

    if not pids:
        log("No saved PIDs found")
        return False

    log(f"Stopping processes: {pids}")

    for pid in pids:
        kill_process_by_pid(pid)

    return True


def cleanup_pid_file():
    """Remove PID file"""
    if PID_FILE.exists():
        PID_FILE.unlink()
        log("PID file removed")


def main():
    """Main entry point"""
    log("SpeechMate Host Server - Stopping...")

    # First try to stop by PID file
    stopped_by_pid = stop_by_pid_file()

    # Also kill any processes on service ports
    kill_port_processes()

    # Clean up PID file
    cleanup_pid_file()

    log("All services stopped")


if __name__ == "__main__":
    main()
