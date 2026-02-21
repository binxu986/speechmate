"""
SpeechMate Client Configuration
"""
import os
import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_FILE = DATA_DIR / "config.json"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)


class HotkeyConfig(BaseModel):
    """Hotkey configuration"""
    transcribe: str = "alt"  # 语音识别快捷键
    translate_zh_to_en: str = "shift"  # 中译英快捷键
    translate_en_to_zh: str = "shift+a"  # 英译中快捷键


class ClientConfig(BaseModel):
    """Client configuration"""
    base_url: str = "http://localhost:8000"
    api_key: str = ""
    hotkeys: HotkeyConfig = HotkeyConfig()
    auto_start: bool = False
    minimize_to_tray: bool = True
    show_recording_indicator: bool = True
    language: str = "auto"  # auto, zh, en


def load_config() -> ClientConfig:
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return ClientConfig(**data)
        except Exception:
            pass
    return ClientConfig()


def save_config(config: ClientConfig):
    """Save configuration to file"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config.model_dump(), f, indent=2, ensure_ascii=False)


# Global config instance
config = load_config()
