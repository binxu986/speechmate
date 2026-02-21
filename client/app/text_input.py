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
    Check if cursor is in a text input field
    This is a heuristic check - returns True if there's an active window
    that might accept text input.
    """
    try:
        if sys.platform == "win32":
            # On Windows, we assume text input is available
            # A more sophisticated check would use UI Automation
            return True
        return True
    except Exception:
        return True


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
