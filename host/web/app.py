"""
SpeechMate Web Admin Server Entry Point
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from web import run_web_server

if __name__ == "__main__":
    run_web_server()
