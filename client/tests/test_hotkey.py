"""
Tests for Client Hotkey Module
Note: Most tests are mocked due to hardware dependencies
"""
import pytest
import sys
from unittest.mock import MagicMock, patch


# Mock hardware-dependent modules before importing
@pytest.fixture(autouse=True)
def mock_hardware_deps():
    """Mock pynput before importing"""
    # Mock pynput
    mock_kb = MagicMock()
    mock_kb.Key = MagicMock()
    mock_kb.Key.alt = "alt"
    mock_kb.Key.alt_l = "alt_l"
    mock_kb.Key.alt_r = "alt_r"
    mock_kb.Key.shift = "shift"
    mock_kb.Key.shift_l = "shift_l"
    mock_kb.Key.shift_r = "shift_r"
    mock_kb.Key.ctrl = "ctrl"
    mock_kb.Key.ctrl_l = "ctrl_l"
    mock_kb.Key.ctrl_r = "ctrl_r"
    mock_kb.Key.cmd = "cmd"
    mock_kb.Listener = MagicMock()
    mock_kb.KeyCode = MagicMock()
    mock_kb.KeyCode.from_char = lambda c: c
    sys.modules['pynput'] = MagicMock()
    sys.modules['pynput.keyboard'] = mock_kb

    yield

    # Cleanup
    sys.modules.pop('pynput', None)
    sys.modules.pop('pynput.keyboard', None)


class TestHotkeyModule:
    """Test hotkey module"""

    def test_import_hotkey(self, mock_hardware_deps):
        """Test that hotkey module can be imported"""
        from app import hotkey
        assert hotkey is not None

    def test_import_hotkey_listener_class(self, mock_hardware_deps):
        """Test that HotkeyListener class is available"""
        from app.hotkey import HotkeyListener
        assert HotkeyListener is not None

    def test_import_hotkey_action_enum(self, mock_hardware_deps):
        """Test that HotkeyAction enum is available"""
        from app.hotkey import HotkeyAction
        assert HotkeyAction is not None


class TestHotkeyActionEnum:
    """Test HotkeyAction enum"""

    def test_transcribe_action(self, mock_hardware_deps):
        """Test TRANSCRIBE action exists"""
        from app.hotkey import HotkeyAction
        assert HotkeyAction.TRANSCRIBE is not None

    def test_translate_zh_to_en_action(self, mock_hardware_deps):
        """Test TRANSLATE_ZH_TO_EN action exists"""
        from app.hotkey import HotkeyAction
        assert HotkeyAction.TRANSLATE_ZH_TO_EN is not None

    def test_translate_en_to_zh_action(self, mock_hardware_deps):
        """Test TRANSLATE_EN_TO_ZH action exists"""
        from app.hotkey import HotkeyAction
        assert HotkeyAction.TRANSLATE_EN_TO_ZH is not None


class TestHotkeyListenerInit:
    """Test HotkeyListener initialization"""

    def test_init(self, mock_hardware_deps):
        """Test default initialization"""
        from app.hotkey import HotkeyListener
        listener = HotkeyListener()
        assert listener._listener is None
        assert listener._callbacks == {}
        assert listener._is_active == False


class TestHotkeyCallback:
    """Test callback functionality"""

    def test_set_callback(self, mock_hardware_deps):
        """Test setting callback"""
        from app.hotkey import HotkeyAction, HotkeyListener

        listener = HotkeyListener()
        callback = MagicMock()
        listener.set_callback(HotkeyAction.TRANSCRIBE, callback)

        assert HotkeyAction.TRANSCRIBE in listener._callbacks
        assert listener._callbacks[HotkeyAction.TRANSCRIBE] == callback

    def test_multiple_callbacks(self, mock_hardware_deps):
        """Test setting multiple callbacks"""
        from app.hotkey import HotkeyAction, HotkeyListener

        listener = HotkeyListener()
        callback1 = MagicMock()
        callback2 = MagicMock()

        listener.set_callback(HotkeyAction.TRANSCRIBE, callback1)
        listener.set_callback(HotkeyAction.TRANSLATE_ZH_TO_EN, callback2)

        assert len(listener._callbacks) == 2


class TestHotkeyPauseResume:
    """Test pause and resume functionality"""

    def test_pause(self, mock_hardware_deps):
        """Test pausing listener"""
        from app.hotkey import HotkeyListener

        listener = HotkeyListener()
        listener._is_active = True
        listener.pause()

        assert listener._is_active == False

    def test_resume(self, mock_hardware_deps):
        """Test resuming listener"""
        from app.hotkey import HotkeyListener

        listener = HotkeyListener()
        listener._is_active = False
        listener.resume()

        assert listener._is_active == True
