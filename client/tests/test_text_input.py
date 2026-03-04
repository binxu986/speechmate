"""
Tests for Client Text Input Module
Note: Most tests are mocked due to hardware dependencies
"""
import pytest
import sys
import platform
from unittest.mock import MagicMock, patch, PropertyMock


# Mock hardware-dependent modules before importing
@pytest.fixture(autouse=True)
def mock_hardware_deps():
    """Mock pyperclip and keyboard before importing"""
    # Mock pyperclip
    mock_pyperclip = MagicMock()
    mock_pyperclip.copy = MagicMock(return_value=True)
    mock_pyperclip.paste = MagicMock(return_value="")
    sys.modules['pyperclip'] = mock_pyperclip

    # Mock keyboard
    mock_keyboard = MagicMock()
    mock_keyboard.press_and_release = MagicMock()
    sys.modules['keyboard'] = mock_keyboard

    yield

    # Cleanup
    sys.modules.pop('pyperclip', None)
    sys.modules.pop('keyboard', None)


class TestTextInputModule:
    """Test text_input module"""

    def test_import_text_input(self, mock_hardware_deps):
        """Test that text_input module can be imported"""
        from app import text_input
        assert text_input is not None

    def test_import_functions(self, mock_hardware_deps):
        """Test that functions are available"""
        from app.text_input import (
            is_text_input_active,
            insert_text_at_cursor,
            copy_to_clipboard,
            output_text
        )
        assert callable(is_text_input_active)
        assert callable(insert_text_at_cursor)
        assert callable(copy_to_clipboard)
        assert callable(output_text)


class TestIsTextInputActive:
    """Test is_text_input_active function"""

    def test_returns_bool(self, mock_hardware_deps):
        """Test that function returns boolean"""
        from app.text_input import is_text_input_active
        result = is_text_input_active()
        assert isinstance(result, bool)

    def test_default_returns_true(self, mock_hardware_deps):
        """Test that default returns True"""
        from app.text_input import is_text_input_active
        result = is_text_input_active()
        assert result == True


class TestCopyToClipboard:
    """Test copy_to_clipboard function"""

    def test_copy_success(self, mock_hardware_deps):
        """Test successful copy to clipboard"""
        from app.text_input import copy_to_clipboard

        result = copy_to_clipboard("test text")
        assert result == True

    def test_copy_chinese_text(self, mock_hardware_deps):
        """Test copying Chinese text"""
        from app.text_input import copy_to_clipboard

        result = copy_to_clipboard("你好世界")
        assert result == True

    def test_copy_empty_text(self, mock_hardware_deps):
        """Test copying empty text"""
        from app.text_input import copy_to_clipboard

        result = copy_to_clipboard("")
        assert result == False


class TestInsertTextAtCursor:
    """Test insert_text_at_cursor function"""

    def test_insert_empty_text(self, mock_hardware_deps):
        """Test inserting empty text"""
        from app.text_input import insert_text_at_cursor

        result = insert_text_at_cursor("")
        assert result == False


class TestOutputText:
    """Test output_text function"""

    def test_output_force_clipboard(self, mock_hardware_deps):
        """Test output with force clipboard"""
        from app.text_input import output_text

        result = output_text("test", force_clipboard=True)
        assert result == True

    def test_output_empty_text(self, mock_hardware_deps):
        """Test output with empty text"""
        from app.text_input import output_text

        result = output_text("")
        assert result == False


class TestClipboardEncoding:
    """Test clipboard encoding for different languages"""

    def test_chinese_encoding(self, mock_hardware_deps):
        """Test Chinese text encoding"""
        from app.text_input import copy_to_clipboard

        chinese_text = "这是一个中文测试"
        result = copy_to_clipboard(chinese_text)
        assert result == True

    def test_japanese_encoding(self, mock_hardware_deps):
        """Test Japanese text encoding"""
        from app.text_input import copy_to_clipboard

        japanese_text = "これは日本語テストです"
        result = copy_to_clipboard(japanese_text)
        assert result == True

    def test_mixed_encoding(self, mock_hardware_deps):
        """Test mixed language encoding"""
        from app.text_input import copy_to_clipboard

        mixed_text = "Hello 世界! 123"
        result = copy_to_clipboard(mixed_text)
        assert result == True


class TestWindowsTextInputDetection:
    """Test Windows-specific text input detection functions"""

    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows only")
    def test_windows_detection_functions_exist(self, mock_hardware_deps):
        """Test that Windows detection functions exist"""
        from app.text_input import _is_text_input_active_windows, _has_caret_position, _has_gui_thread_info
        assert callable(_is_text_input_active_windows)
        assert callable(_has_caret_position)
        assert callable(_has_gui_thread_info)

    def test_windows_detection_returns_bool(self, mock_hardware_deps):
        """Test that Windows detection returns boolean"""
        from app.text_input import _is_text_input_active_windows
        # Mock ctypes to avoid actual Windows calls
        with patch('ctypes.windll.user32.GetForegroundWindow', return_value=0):
            result = _is_text_input_active_windows()
            assert isinstance(result, bool)

    def test_windows_detection_no_foreground_window(self, mock_hardware_deps):
        """Test detection when no foreground window exists"""
        from app.text_input import _is_text_input_active_windows
        with patch('ctypes.windll.user32.GetForegroundWindow', return_value=0):
            result = _is_text_input_active_windows()
            assert result == False

    def test_windows_detection_text_class_detected(self, mock_hardware_deps):
        """Test detection when window class is a text input type"""
        from app.text_input import _is_text_input_active_windows

        mock_user32 = MagicMock()
        mock_user32.GetForegroundWindow.return_value = 12345  # Valid window handle
        mock_user32.GetClassNameW.return_value = 0  # Will be patched

        # Create a unicode buffer mock that returns "Edit"
        with patch('ctypes.windll.user32', mock_user32):
            with patch('ctypes.create_unicode_buffer') as mock_buffer:
                mock_buf = MagicMock()
                mock_buf.value = "Edit"
                mock_buffer.return_value = mock_buf

                result = _is_text_input_active_windows()
                assert result == True

    def test_caret_detection_returns_bool(self, mock_hardware_deps):
        """Test that caret detection returns boolean"""
        from app.text_input import _has_caret_position
        result = _has_caret_position()
        assert isinstance(result, bool)

    def test_caret_detection_failure_returns_false(self, mock_hardware_deps):
        """Test that caret detection returns False on failure"""
        from app.text_input import _has_caret_position

        # Mock GetForegroundWindow to return 0 (no window)
        # This should cause the function to return False
        mock_user32 = MagicMock()
        mock_user32.GetForegroundWindow.return_value = 0
        mock_user32.GetWindowThreadProcessId.return_value = 0
        mock_kernel32 = MagicMock()
        mock_kernel32.GetCurrentThreadId.return_value = 1
        mock_user32.AttachThreadInput.return_value = False  # Attach fails

        with patch('ctypes.windll.user32', mock_user32):
            with patch('ctypes.windll.kernel32', mock_kernel32):
                result = _has_caret_position()
                assert result == False

    def test_gui_thread_info_returns_bool(self, mock_hardware_deps):
        """Test that GUI thread info returns boolean"""
        from app.text_input import _has_gui_thread_info
        result = _has_gui_thread_info()
        assert isinstance(result, bool)

    def test_gui_thread_info_failure_returns_false(self, mock_hardware_deps):
        """Test that GUI thread info returns False on failure"""
        from app.text_input import _has_gui_thread_info

        mock_user32 = MagicMock()
        mock_user32.GetGUIThreadInfo.return_value = 0  # Failure

        with patch('ctypes.windll.user32', mock_user32):
            result = _has_gui_thread_info()
            assert result == False


class TestOutputTextBehavior:
    """Test output_text behavior with text input detection"""

    def test_output_text_falls_back_to_clipboard_on_detection_failure(self, mock_hardware_deps):
        """Test that output_text falls back to clipboard when insertion fails"""
        from app.text_input import output_text

        # Mock is_text_input_active to return True (text input active)
        # Mock insert_text_at_cursor to return False (insertion fails)
        with patch('app.text_input.is_text_input_active', return_value=True):
            with patch('app.text_input.insert_text_at_cursor', return_value=False):
                result = output_text("test text")
                # Should fall back to clipboard and return True
                assert result == True

    def test_output_text_uses_clipboard_when_no_text_input(self, mock_hardware_deps):
        """Test that output_text uses clipboard when no text input is active"""
        from app.text_input import output_text

        with patch('app.text_input.is_text_input_active', return_value=False):
            with patch('app.text_input.copy_to_clipboard', return_value=True) as mock_copy:
                result = output_text("test text")
                assert result == True
                mock_copy.assert_called_once_with("test text")

    def test_output_text_uses_insertion_when_text_input_active(self, mock_hardware_deps):
        """Test that output_text tries insertion when text input is active"""
        from app.text_input import output_text

        with patch('app.text_input.is_text_input_active', return_value=True):
            with patch('app.text_input.insert_text_at_cursor', return_value=True) as mock_insert:
                result = output_text("test text")
                assert result == True
                mock_insert.assert_called_once_with("test text")

    def test_output_text_force_clipboard_bypasses_detection(self, mock_hardware_deps):
        """Test that force_clipboard=True bypasses text input detection"""
        from app.text_input import output_text

        with patch('app.text_input.is_text_input_active', return_value=True):
            with patch('app.text_input.copy_to_clipboard', return_value=True) as mock_copy:
                with patch('app.text_input.insert_text_at_cursor') as mock_insert:
                    result = output_text("test text", force_clipboard=True)
                    assert result == True
                    mock_copy.assert_called_once()
                    mock_insert.assert_not_called()


class TestInsertTextAtCursor:
    """Test insert_text_at_cursor function more thoroughly"""

    def test_insert_returns_true_on_success(self, mock_hardware_deps):
        """Test that insert returns True on successful insertion"""
        from app.text_input import insert_text_at_cursor

        result = insert_text_at_cursor("test text")
        assert result == True

    def test_insert_handles_chinese_text(self, mock_hardware_deps):
        """Test that insert handles Chinese text"""
        from app.text_input import insert_text_at_cursor

        result = insert_text_at_cursor("你好世界")
        assert result == True

    def test_insert_handles_special_characters(self, mock_hardware_deps):
        """Test that insert handles special characters"""
        from app.text_input import insert_text_at_cursor

        result = insert_text_at_cursor("Hello! @#$%^&*() 你好")
        assert result == True

    def test_insert_handles_multiline_text(self, mock_hardware_deps):
        """Test that insert handles multiline text"""
        from app.text_input import insert_text_at_cursor

        result = insert_text_at_cursor("Line 1\nLine 2\nLine 3")
        assert result == True

    def test_insert_handles_long_text(self, mock_hardware_deps):
        """Test that insert handles long text"""
        from app.text_input import insert_text_at_cursor

        long_text = "A" * 10000
        result = insert_text_at_cursor(long_text)
        assert result == True
