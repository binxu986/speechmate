"""
SpeechMate Client Logger Configuration
"""
import sys
from pathlib import Path
from loguru import logger

# Remove default handler
logger.remove()

# Add console handler
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)

# Add file handler
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

logger.add(
    log_dir / "speechmate_client_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    level="DEBUG",
    encoding="utf-8"
)


def get_logger(name: str):
    """Get logger instance"""
    return logger.bind(name=name)
