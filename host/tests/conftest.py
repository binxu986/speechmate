"""
pytest configuration and fixtures for SpeechMate tests
"""
import sys
import os
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add host directory to path for imports
host_dir = Path(__file__).parent.parent
sys.path.insert(0, str(host_dir))

from app.database import Base, APIKey
from app.config import config


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
def sample_audio_zh_path(test_data_dir):
    """Path to Chinese audio file for testing"""
    audio_path = test_data_dir / "test_audio_zh.wav"
    if not audio_path.exists():
        pytest.skip(f"Test audio file not found: {audio_path}")
    return str(audio_path)


@pytest.fixture
def sample_audio_short_path(test_data_dir):
    """Path to short audio file for boundary testing"""
    audio_path = test_data_dir / "test_audio_short.wav"
    if not audio_path.exists():
        pytest.skip(f"Test audio file not found: {audio_path}")
    return str(audio_path)


@pytest.fixture
def sample_audio_silent_path(test_data_dir):
    """Path to silent audio file for boundary testing"""
    audio_path = test_data_dir / "test_audio_silent.wav"
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
        ),
        database=DatabaseConfig(
            db_path=":memory:"  # Use in-memory database for tests
        )
    )


@pytest.fixture
def mock_api_key():
    """Mock API key for testing"""
    return "test_api_key_12345678abcdef"


@pytest.fixture
def mock_audio_bytes():
    """Mock audio bytes for testing"""
    # Return minimal valid WAV header + some data
    return b"RIFF" + b"\x24\x00\x00\x00" + b"WAVE" + b"fmt " + b"\x10\x00\x00\x00" + \
           b"\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00" + \
           b"data" + b"\x00\x00\x00\x00"


@pytest.fixture(scope="function")
def isolated_db():
    """Create an isolated test database for each test"""
    # Create temporary database file
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        # Create a default test key
        session = SessionLocal()
        test_key = APIKey(
            key="test_default_key_12345678",
            name="Test Default Key",
            is_active=True
        )
        session.add(test_key)
        session.commit()
        session.close()

        yield {"db_path": db_path, "engine": engine, "SessionLocal": SessionLocal}

        # Cleanup
        engine.dispose()
        try:
            os.unlink(db_path)
        except:
            pass
