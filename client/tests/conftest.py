"""
Client Test Fixtures
"""
import pytest
import sys
from pathlib import Path

# Add client directory to path
client_dir = Path(__file__).parent.parent
sys.path.insert(0, str(client_dir))


@pytest.fixture
def mock_api_response():
    """Mock API response for testing"""
    return {
        "success": True,
        "text": "Hello, world!",
        "language": "en",
        "duration": 3.5
    }


@pytest.fixture
def mock_transcribe_response():
    """Mock transcribe response"""
    return {
        "success": True,
        "text": "This is a test transcription.",
        "language": "en"
    }


@pytest.fixture
def sample_audio_path():
    """Path to a sample audio file for testing"""
    # Use a fixture from host if available
    host_fixture = client_dir.parent / "host" / "tests" / "fixtures" / "test_audio.wav"
    if host_fixture.exists():
        return str(host_fixture)
    return None
