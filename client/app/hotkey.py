"""
SpeechMate Hotkey Listener Module
"""
import threading
from typing import Callable, Optional
from enum import Enum, auto
from functools import partial

from pynput import keyboard
from loguru import logger


class HotkeyAction(Enum):
    """Hotkey actions"""
    TRANSCRIBE = auto()  # 语音识别
    TRANSLATE_ZH_TO_EN = auto()  # 中译英
    TRANSLATE_EN_TO_ZH = auto()  # 英译中


class HotkeyListener:
    """Global hotkey listener"""

    def __init__(self):
        self._listener: Optional[keyboard.Listener] = None
        self._callbacks: dict = {}
        self._pressed_keys: set = set()
        self._is_active = False

        # Key mapping
        self._key_map = {
            "alt": {keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r},
            "shift": {keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r},
            "ctrl": {keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r},
            "cmd": {keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r},
        }

    def set_callback(self, action: HotkeyAction, callback: Callable):
        """Set callback for hotkey action"""
        self._callbacks[action] = callback

    def _parse_hotkey(self, hotkey_str: str) -> tuple:
        """Parse hotkey string to key set"""
        keys = set()
        parts = hotkey_str.lower().replace(" ", "").split("+")

        for part in parts:
            if part in self._key_map:
                keys.update(self._key_map[part])
            elif len(part) == 1:
                keys.add(keyboard.KeyCode.from_char(part))
            else:
                # Try as special key
                try:
                    key = getattr(keyboard.Key, part, None)
                    if key:
                        keys.add(key)
                except:
                    pass

        return frozenset(keys)

    def _check_hotkey(self, hotkey_str: str) -> bool:
        """Check if hotkey is currently pressed"""
        target_keys = self._parse_hotkey(hotkey_str)
        return target_keys.issubset(self._pressed_keys)

    def _on_press(self, key):
        """Handle key press"""
        self._pressed_keys.add(key)

        # Check hotkeys
        if not self._is_active:
            return

        # Get current config
        from app.config import config

        transcribe_key = config.hotkeys.transcribe
        translate_zh_en_key = config.hotkeys.translate_zh_to_en
        translate_en_zh_key = config.hotkeys.translate_en_to_zh

        # Check which hotkey is pressed
        if self._check_hotkey(translate_en_zh_key):
            self._trigger_action(HotkeyAction.TRANSLATE_EN_TO_ZH)
        elif self._check_hotkey(translate_zh_en_key):
            # Make sure shift+a is not triggered when just shift is pressed
            if "a" not in translate_zh_en_key.lower() or "a" in translate_en_zh_key.lower():
                self._trigger_action(HotkeyAction.TRANSLATE_ZH_TO_EN)
        elif self._check_hotkey(transcribe_key):
            self._trigger_action(HotkeyAction.TRANSCRIBE)

    def _on_release(self, key):
        """Handle key release"""
        self._pressed_keys.discard(key)

    def _trigger_action(self, action: HotkeyAction):
        """Trigger hotkey action callback"""
        if action in self._callbacks:
            try:
                callback = self._callbacks[action]
                # Run in separate thread to avoid blocking
                threading.Thread(target=callback, daemon=True).start()
            except Exception as e:
                logger.error(f"Hotkey callback error: {e}")

    def start(self):
        """Start listening for hotkeys"""
        if self._listener and self._listener.is_alive():
            return

        self._is_active = True
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self._listener.daemon = True
        self._listener.start()
        logger.info("Hotkey listener started")

    def stop(self):
        """Stop listening for hotkeys"""
        self._is_active = False
        if self._listener:
            self._listener.stop()
            self._listener = None
        logger.info("Hotkey listener stopped")

    def pause(self):
        """Pause hotkey detection"""
        self._is_active = False

    def resume(self):
        """Resume hotkey detection"""
        self._is_active = True


# Global hotkey listener instance
hotkey_listener = HotkeyListener()
