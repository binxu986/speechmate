"""
SpeechMate Hotkey Listener Module
Uses keyboard library with hook for better modifier key support
"""
import threading
from typing import Callable, Optional
from enum import Enum, auto

from loguru import logger
import keyboard


class HotkeyAction(Enum):
    """Hotkey actions"""
    TRANSCRIBE = auto()  # 语音识别
    TRANSLATE_ZH_TO_EN = auto()  # 中译英
    TRANSLATE_EN_TO_ZH = auto()  # 英译中


class HotkeyListener:
    """Global hotkey listener using keyboard library hooks"""

    def __init__(self):
        self._hook = None
        self._callbacks: dict = {}
        self._is_active = False
        self._pressed_keys: set = set()
        self._action_triggered: set = set()  # Track which actions have been triggered

    def set_callback(self, action: HotkeyAction, callback: Callable):
        """Set callback for hotkey action"""
        self._callbacks[action] = callback

    def _parse_hotkey(self, hotkey_str: str) -> set:
        """Parse hotkey string to key set"""
        keys = set()
        parts = hotkey_str.lower().replace(" ", "").split("+")

        for part in parts:
            if part in ("alt", "left alt", "right alt"):
                keys.add("alt")
            elif part in ("shift", "left shift", "right shift"):
                keys.add("shift")
            elif part in ("ctrl", "left ctrl", "right ctrl", "control"):
                keys.add("ctrl")
            else:
                keys.add(part.lower())

        return keys

    def _get_current_keys(self) -> set:
        """Get currently pressed keys"""
        keys = set()
        if keyboard.is_pressed('alt'):
            keys.add('alt')
        if keyboard.is_pressed('shift'):
            keys.add('shift')
        if keyboard.is_pressed('ctrl'):
            keys.add('ctrl')

        # Check for letter keys
        for char in 'abcdefghijklmnopqrstuvwxyz':
            if keyboard.is_pressed(char):
                keys.add(char)

        # Check for F keys (f1-f24)
        for i in range(1, 25):
            if keyboard.is_pressed(f'f{i}'):
                keys.add(f'f{i}')

        return keys

    def _check_hotkey(self, hotkey_str: str) -> bool:
        """Check if hotkey is currently pressed"""
        target_keys = self._parse_hotkey(hotkey_str)
        current_keys = self._get_current_keys()
        return target_keys.issubset(current_keys)

    def _on_key_event(self, event):
        """Handle keyboard event"""
        if not self._is_active:
            return

        from app.config import config

        key_name = event.name.lower()

        # On key up, reset the triggered state for this key
        if event.event_type == keyboard.KEY_UP:
            # Reset triggered actions when any hotkey key is released
            transcribe_key = config.hotkeys.transcribe.lower()
            translate_zh_en_key = config.hotkeys.translate_zh_to_en.lower()
            translate_en_zh_key = config.hotkeys.translate_en_to_zh.lower()

            if key_name in (transcribe_key, "alt", "left alt", "right alt"):
                self._action_triggered.discard(HotkeyAction.TRANSCRIBE)
            if key_name in (translate_zh_en_key, "shift", "left shift", "right shift"):
                self._action_triggered.discard(HotkeyAction.TRANSLATE_ZH_TO_EN)
            if key_name in (translate_en_zh_key.split('+')[-1], "shift", "a"):
                self._action_triggered.discard(HotkeyAction.TRANSLATE_EN_TO_ZH)
            return

        # Only process key down events
        if event.event_type != keyboard.KEY_DOWN:
            return

        transcribe_key = config.hotkeys.transcribe.lower()
        translate_zh_en_key = config.hotkeys.translate_zh_to_en.lower()
        translate_en_zh_key = config.hotkeys.translate_en_to_zh.lower()

        # Only trigger if this specific key matches the hotkey
        if key_name == transcribe_key or key_name in transcribe_key:
            if HotkeyAction.TRANSCRIBE not in self._action_triggered:
                self._action_triggered.add(HotkeyAction.TRANSCRIBE)
                self._trigger_action(HotkeyAction.TRANSCRIBE)
        elif key_name == translate_en_zh_key.split('+')[-1] and self._check_hotkey(translate_en_zh_key):
            if HotkeyAction.TRANSLATE_EN_TO_ZH not in self._action_triggered:
                self._action_triggered.add(HotkeyAction.TRANSLATE_EN_TO_ZH)
                self._trigger_action(HotkeyAction.TRANSLATE_EN_TO_ZH)
        elif key_name == translate_zh_en_key:
            if HotkeyAction.TRANSLATE_ZH_TO_EN not in self._action_triggered:
                self._action_triggered.add(HotkeyAction.TRANSLATE_ZH_TO_EN)
                self._trigger_action(HotkeyAction.TRANSLATE_ZH_TO_EN)

    def _trigger_action(self, action: HotkeyAction):
        """Trigger hotkey action callback"""
        if action in self._callbacks:
            try:
                callback = self._callbacks[action]
                logger.info(f"Hotkey triggered: {action.name}")
                # Run in separate thread to avoid blocking
                threading.Thread(target=callback, daemon=True).start()
            except Exception as e:
                logger.error(f"Hotkey callback error: {e}")

    def start(self):
        """Start listening for hotkeys"""
        if self._is_active:
            return

        self._is_active = True
        self._hook = keyboard.hook(self._on_key_event)
        logger.info("Hotkey listener started (hook mode)")

    def stop(self):
        """Stop listening for hotkeys"""
        self._is_active = False
        if self._hook:
            keyboard.unhook(self._hook)
            self._hook = None
        logger.info("Hotkey listener stopped")

    def pause(self):
        """Pause hotkey detection"""
        self._is_active = False

    def resume(self):
        """Resume hotkey detection"""
        self._is_active = True


# Global hotkey listener instance
hotkey_listener = HotkeyListener()
