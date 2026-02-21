"""
SpeechMate Host Server Configuration
"""
import os
import secrets
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "model_cache"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for dir_path in [DATA_DIR, MODELS_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


class ServerConfig(BaseModel):
    """Server configuration"""
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    web_host: str = "0.0.0.0"
    web_port: int = 5000
    debug: bool = False


class ModelConfig(BaseModel):
    """Model configuration"""
    asr_model: str = "small"
    asr_device: str = "cpu"  # cpu or cuda
    asr_compute_type: str = "int8"  # float16, int8, int8_float16
    translation_model_zh_en: str = "Helsinki-NLP/opus-mt-zh-en"
    translation_model_en_zh: str = "Helsinki-NLP/opus-mt-en-zh"


class DatabaseConfig(BaseModel):
    """Database configuration"""
    db_path: str = str(DATA_DIR / "speechmate.db")


class Config(BaseModel):
    """Main configuration"""
    server: ServerConfig = ServerConfig()
    model: ModelConfig = ModelConfig()
    database: DatabaseConfig = DatabaseConfig()

    # Admin settings
    admin_api_key: str = os.getenv("ADMIN_API_KEY", secrets.token_hex(16))
    jwt_secret: str = os.getenv("JWT_SECRET", secrets.token_hex(32))


# Global config instance
config = Config()


# Available ASR models
ASR_MODELS = {
    "tiny": {
        "name": "faster-whisper-tiny",
        "size": "39MB",
        "speed": "极快",
        "accuracy": "一般",
        "description": "最快的模型，适合快速响应场景"
    },
    "base": {
        "name": "faster-whisper-base",
        "size": "74MB",
        "speed": "快",
        "accuracy": "较好",
        "description": "速度和精度的平衡选择"
    },
    "small": {
        "name": "faster-whisper-small",
        "size": "244MB",
        "speed": "中等",
        "accuracy": "好",
        "description": "推荐的默认选择"
    },
    "medium": {
        "name": "faster-whisper-medium",
        "size": "769MB",
        "speed": "较慢",
        "accuracy": "很好",
        "description": "高精度识别"
    },
    "large-v3": {
        "name": "faster-whisper-large-v3",
        "size": "1.5GB",
        "speed": "慢",
        "accuracy": "最好",
        "description": "最高精度的模型"
    }
}


def get_base_url() -> str:
    """Get the base URL for API access"""
    return f"http://{get_local_ip()}:{config.server.api_port}"


def get_local_ip() -> str:
    """Get local IP address"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def save_config():
    """Save configuration to file"""
    import yaml
    config_path = DATA_DIR / "config.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config.model_dump(), f, default_flow_style=False, allow_unicode=True)


def load_config_from_file():
    """Load configuration from file"""
    import yaml
    config_path = DATA_DIR / "config.yaml"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data:
                global config
                config = Config(**data)
