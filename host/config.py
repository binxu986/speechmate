import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "config.json"
MODELS_DIR = BASE_DIR / "models"

DEFAULT_CONFIG = {
    "host": "0.0.0.0",
    "port": 3456,
    "asr_model": "base",
    "translate_model": "m2m100-418M",
    "device": "cpu",
    "api_keys": [],
    "stats": {}
}

def load_config():
    import json
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG.copy()

def save_config(config):
    import json
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
