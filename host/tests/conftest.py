"""
pytest configuration and fixtures for SpeechMate tests
"""
import sys
import os
from pathlib import Path

import pytest

# Add host directory to path for imports
host_dir = Path(__file__).parent.parent
sys.path.insert(0, str(host_dir))


@pytest.fixture
def test_data_dir():
    """Directory containing test data files"""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_audio_path(test_data_dir):
    """Path to sample audio file for testing"""
    audio_path = test_data_dir / "test_audio.wav"
    if not audio_path.exists():
        pytest.skip(f"Test audio file not found: {audio_path}")
    return str(audio_path)


@pytest.fixture
def temp_db_path(tmp_path):
    """Temporary database path for testing"""
    return str(tmp_path / "test_speechmate.db")


@pytest.fixture
def test_config():
    """Test configuration"""
    from app.config import Config, ServerConfig, ModelConfig, DatabaseConfig
    return Config(
        server=ServerConfig(
            api_host="127.0.0.1",
            api_port=8000,
            web_host="127.0.0.1",
            web_port=5000,
            debug=True
        ),
        model=ModelConfig(
            asr_model="tiny",  # Use smallest model for tests
            asr_device="cpu",
            asr_compute_type="int8"
        )
    )