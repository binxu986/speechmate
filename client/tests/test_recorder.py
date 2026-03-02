"""
Tests for Client Recorder Module
Note: Most tests are mocked due to hardware dependencies
"""
import pytest
import sys
from unittest.mock import MagicMock, patch


# Mock hardware-dependent modules before importing
@pytest.fixture(autouse=True)
def mock_hardware_deps():
    """Mock sounddevice and numpy before importing"""
    # Mock numpy
    mock_np = MagicMock()
    mock_np.zeros = lambda *args, **kwargs: []
    mock_np.concatenate = lambda *args, **kwargs: []
    mock_np.float32 = 'float32'
    sys.modules['numpy'] = mock_np

    # Mock sounddevice
    mock_sd = MagicMock()
    mock_sd.query_devices.return_value = []
    mock_sd.InputStream = MagicMock()
    sys.modules['sounddevice'] = mock_sd

    yield

    # Cleanup
    sys.modules.pop('numpy', None)
    sys.modules.pop('sounddevice', None)


class TestRecorderBasic:
    """Basic recorder tests"""

    def test_recorder_module_structure(self, mock_hardware_deps):
        """Test recorder module can be imported"""
        from app.recorder import AudioRecorder, recorder
        assert AudioRecorder is not None
        assert recorder is not None

    def test_recorder_default_config(self, mock_hardware_deps):
        """Test recorder default configuration"""
        from app.recorder import AudioRecorder
        rec = AudioRecorder()
        assert rec.sample_rate == 16000
        assert rec.channels == 1
        assert rec.dtype == "float32"

    def test_recorder_custom_config(self, mock_hardware_deps):
        """Test recorder custom configuration"""
        from app.recorder import AudioRecorder
        rec = AudioRecorder(sample_rate=44100, channels=2, dtype="int16")
        assert rec.sample_rate == 44100
        assert rec.channels == 2
        assert rec.dtype == "int16"

    def test_recorder_initial_state(self, mock_hardware_deps):
        """Test recorder initial state"""
        from app.recorder import AudioRecorder
        rec = AudioRecorder()
        assert rec.is_recording == False

    def test_recorder_state_callback(self, mock_hardware_deps):
        """Test state callback setting"""
        from app.recorder import AudioRecorder
        callback = MagicMock()
        rec = AudioRecorder()
        rec.set_state_callback(callback)
        assert rec._on_state_change == callback


class TestRecorderDevices:
    """Test device enumeration"""

    def test_get_input_devices(self, mock_hardware_deps):
        """Test getting input devices"""
        from app.recorder import AudioRecorder
        rec = AudioRecorder()
        devices = rec.get_input_devices()
        assert isinstance(devices, list)


class TestRecorderFormat:
    """Test recording format"""

    def test_sample_rate_speech(self, mock_hardware_deps):
        """Test sample rate is 16kHz for speech"""
        from app.recorder import AudioRecorder
        rec = AudioRecorder()
        assert rec.sample_rate == 16000

    def test_channels_mono(self, mock_hardware_deps):
        """Test channels is mono"""
        from app.recorder import AudioRecorder
        rec = AudioRecorder()
        assert rec.channels == 1
