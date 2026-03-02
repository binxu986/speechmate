"""
Tests for Client Text Input Module
Note: Most tests are mocked due to hardware dependencies
"""
import pytest
import sys
from unittest.mock import MagicMock, patch


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
