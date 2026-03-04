"""
SpeechMate Text Input Module
Handles text insertion at cursor position or clipboard
"""
import subprocess
import sys
import time
from typing import Optional

import pyperclip
from loguru import logger


def is_text_input_active() -> bool:
    """
    Check if cursor is in a text input field.

    On Windows, uses multiple methods to detect if the focused element
    accepts text input. Falls back to True if detection fails.

    Returns:
        True if a text input field is active, False otherwise
    """
    try:
        if sys.platform == "win32":
            return _is_text_input_active_windows()
        # For other platforms, assume text input is available
        return True
    except Exception as e:
        logger.debug(f"Text input detection failed: {e}")
        return True


def _is_text_input_active_windows() -> bool:
    """
    Windows-specific check for text input field.

    Uses multiple detection methods:
    1. Check for caret (text cursor) position
    2. Check window class name for known text input controls

    Returns:
        True if text input field is active, False otherwise
    """
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32

        # Get the foreground window
        foreground_window = user32.GetForegroundWindow()

        if not foreground_window:
            return False

        # Method 1: Check window class name
        # Many text input controls have identifiable class names
        buffer_size = 256
        buffer = ctypes.create_unicode_buffer(buffer_size)
        user32.GetClassNameW(foreground_window, buffer, buffer_size)
        class_name = buffer.value.lower()

        # Known text input window classes
        text_input_classes = [
            "edit",           # Standard Windows edit control
            "richtext",       # Rich text controls
            "textedit",       # Qt text edit
            "qlineedit",      # Qt line edit
            "qtextedit",      # Qt text edit
            "qplaintextedit", # Qt plain text edit
            "chrome_omniboxview",  # Chrome address bar
            "chrome_widgetwin",    # Chrome
            "scintilla",      # Notepad++, etc.
            "tscrawler",      # Some terminal emulators
            "windowclass",    # Generic (need more checks)
        ]

        # Check if the window class suggests text input capability
        for text_class in text_input_classes:
            if text_class in class_name:
                logger.debug(f"Text input window class detected: {class_name}")
                return True

        # Method 2: Check for caret position (works for many applications)
        if _has_caret_position():
            return True

        # Method 3: Try to detect using GUITHREADINFO
        if _has_gui_thread_info():
            return True

        # Default: assume no text input active
        logger.debug("No text input field detected")
        return False

    except Exception as e:
        logger.debug(f"Windows text input detection failed: {e}")
        return True


def _has_caret_position() -> bool:
    """
    Check if there's a caret (text cursor) visible in the foreground window.

    This method uses AttachThreadInput to read caret position from
    the foreground window's thread.

    Returns:
        True if a caret position can be detected, False otherwise
    """
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        # Create a point structure for GetCaretPos
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

        point = POINT()

        # Get foreground window's thread
        foreground_window = user32.GetForegroundWindow()
        foreground_thread = user32.GetWindowThreadProcessId(foreground_window, None)

        # Get current thread
        current_thread = kernel32.GetCurrentThreadId()

        # Attach threads to read caret position
        attached = user32.AttachThreadInput(current_thread, foreground_thread, True)
        if attached:
            try:
                # Get the focus window (might be different from foreground)
                focus_window = user32.GetFocus()

                # Try to get caret position from focus window
                result = user32.GetCaretPos(ctypes.byref(point))
                if result:
                    # Caret exists, text input is likely active
                    logger.debug(f"Caret position detected: ({point.x}, {point.y})")
                    return True
            finally:
                user32.AttachThreadInput(current_thread, foreground_thread, False)

        return False

    except Exception as e:
        logger.debug(f"Caret position check failed: {e}")
        return False


def _has_gui_thread_info() -> bool:
    """
    Check for text input using GUITHREADINFO structure.

    This provides information about the active window's state,
    including whether it has a caret.

    Returns:
        True if GUI thread info suggests text input capability
    """
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32

        # GUITHREADINFO structure
        class GUITHREADINFO(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.DWORD),
                ("flags", wintypes.DWORD),
                ("hwndActive", wintypes.HWND),
                ("hwndFocus", wintypes.HWND),
                ("hwndCapture", wintypes.HWND),
                ("hwndMenuOwner", wintypes.HWND),
                ("hwndMoveSize", wintypes.HWND),
                ("hwndCaret", wintypes.HWND),
                ("rcCaret", wintypes.RECT),
            ]

        gui_info = GUITHREADINFO()
        gui_info.cbSize = ctypes.sizeof(GUITHREADINFO)

        # Get GUI thread info for foreground window
        foreground_window = user32.GetForegroundWindow()
        foreground_thread = user32.GetWindowThreadProcessId(foreground_window, None)

        result = user32.GetGUIThreadInfo(foreground_thread, ctypes.byref(gui_info))

        if result:
            # Check if there's a caret window
            if gui_info.hwndCaret:
                logger.debug("Caret window found via GUITHREADINFO")
                return True

            # Check if there's a focused window (indicates potential input)
            if gui_info.hwndFocus:
                # Get class name of focused window
                buffer_size = 256
                buffer = ctypes.create_unicode_buffer(buffer_size)
                user32.GetClassNameW(gui_info.hwndFocus, buffer, buffer_size)
                class_name = buffer.value.lower()

                # Check for text input controls
                if any(c in class_name for c in ["edit", "text", "input", "rich"]):
                    logger.debug(f"Text input focus detected: {class_name}")
                    return True

        return False

    except Exception as e:
        logger.debug(f"GUITHREADINFO check failed: {e}")
        return False


def insert_text_at_cursor(text: str) -> bool:
    """
    Insert text at the current cursor position

    Args:
        text: Text to insert

    Returns:
        True if successful, False otherwise
    """
    if not text:
        return False

    try:
        if sys.platform == "win32":
            # On Windows, use clipboard paste simulation
            # Save current clipboard content
            try:
                old_clipboard = pyperclip.paste()
            except:
                old_clipboard = ""

            # Set new text to clipboard
            pyperclip.copy(text)

            # Small delay to ensure clipboard is updated
            time.sleep(0.05)

            # Simulate Ctrl+V paste
            import keyboard
            keyboard.press_and_release("ctrl+v")

            # Restore original clipboard after a short delay
            time.sleep(0.1)
            try:
                pyperclip.copy(old_clipboard)
            except:
                pass

            return True

        elif sys.platform == "darwin":
            # On macOS, use pbcopy and osascript
            pyperclip.copy(text)
            subprocess.run([
                "osascript", "-e",
                'tell application "System Events" to keystroke "v" using command down'
            ])
            return True

        else:
            # On Linux, use xdotool or similar
            pyperclip.copy(text)
            subprocess.run(["xdotool", "key", "ctrl+v"])
            return True

    except Exception as e:
        logger.error(f"Failed to insert text: {e}")
        return False


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to clipboard

    Args:
        text: Text to copy

    Returns:
        True if successful, False otherwise
    """
    if not text:
        return False

    try:
        pyperclip.copy(text)
        logger.info(f"Copied to clipboard: {text[:50]}...")
        return True
    except Exception as e:
        logger.error(f"Failed to copy to clipboard: {e}")
        return False


def output_text(text: str, force_clipboard: bool = False) -> bool:
    """
    Output text - either insert at cursor or copy to clipboard

    Args:
        text: Text to output
        force_clipboard: If True, always copy to clipboard

    Returns:
        True if successful
    """
    if not text:
        return False

    if force_clipboard or not is_text_input_active():
        return copy_to_clipboard(text)
    else:
        success = insert_text_at_cursor(text)
        if not success:
            # Fallback to clipboard
            return copy_to_clipboard(text)
        return success
