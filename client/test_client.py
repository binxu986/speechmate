#!/usr/bin/env python3
"""
SpeechMate Client Test Script
Tests basic functionality without running the GUI
"""
import sys
from pathlib import Path

# Add client directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test all imports"""
    print("Testing imports...")

    try:
        from app.config import config, save_config
        print("  ✓ app.config")
    except Exception as e:
        print(f"  ✗ app.config: {e}")
        return False

    try:
        from app.api_client import api_client
        print("  ✓ app.api_client")
    except Exception as e:
        print(f"  ✗ app.api_client: {e}")
        return False

    try:
        from app.recorder import recorder
        print("  ✓ app.recorder")
    except Exception as e:
        print(f"  ✗ app.recorder: {e}")
        return False

    try:
        from app.text_input import output_text, copy_to_clipboard
        print("  ✓ app.text_input")
    except Exception as e:
        print(f"  ✗ app.text_input: {e}")
        return False

    try:
        from app.hotkey import hotkey_listener, HotkeyAction
        print("  ✓ app.hotkey")
    except Exception as e:
        print(f"  ✗ app.hotkey: {e}")
        return False

    return True


def test_audio_devices():
    """Test audio device enumeration"""
    print("\nTesting audio devices...")

    try:
        from app.recorder import recorder

        devices = recorder.get_input_devices()
        print(f"  ✓ Found {len(devices)} input devices:")
        for dev in devices[:3]:  # Show first 3
            print(f"    - {dev['name']}")
        if len(devices) > 3:
            print(f"    ... and {len(devices) - 3} more")

        return True
    except Exception as e:
        print(f"  ✗ Audio device error: {e}")
        return False


def test_clipboard():
    """Test clipboard functionality"""
    print("\nTesting clipboard...")

    try:
        from app.text_input import copy_to_clipboard
        import pyperclip

        test_text = "SpeechMate Test"
        copy_to_clipboard(test_text)

        # Verify
        read_text = pyperclip.paste()
        if read_text == test_text:
            print(f"  ✓ Clipboard working: '{read_text}'")
            return True
        else:
            print(f"  ✗ Clipboard mismatch: expected '{test_text}', got '{read_text}'")
            return False

    except Exception as e:
        print(f"  ✗ Clipboard error: {e}")
        return False


def test_config():
    """Test configuration"""
    print("\nTesting configuration...")

    try:
        from app.config import config, save_config, ClientConfig, HotkeyConfig

        # Check default values
        assert config.base_url == "http://localhost:8000"
        assert config.hotkeys.transcribe == "alt"
        assert config.hotkeys.translate_zh_to_en == "shift"
        assert config.hotkeys.translate_en_to_zh == "shift+a"

        print("  ✓ Configuration defaults correct")

        # Test save
        save_config(config)
        print("  ✓ Configuration saved")

        return True

    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False


def test_api_client():
    """Test API client"""
    print("\nTesting API client...")

    try:
        from app.api_client import api_client

        # Test with default URL
        api_client.set_base_url("http://localhost:8000")
        api_client.set_api_key("test_key")

        print(f"  ✓ API client configured: {api_client.base_url}")

        # Note: Actual connection test requires running server
        print("  ℹ Server connection test skipped (server not running)")

        return True

    except Exception as e:
        print(f"  ✗ API client error: {e}")
        return False


def test_recording():
    """Test recording functionality"""
    print("\nTesting recording (brief)...")

    try:
        import time
        from app.recorder import recorder

        # Start recording
        recorder.start_recording()
        print("  ✓ Recording started")

        # Record briefly
        time.sleep(0.5)

        # Stop recording (result will be None for short audio)
        result = recorder.stop_recording()
        if result is None:
            print("  ✓ Recording stopped (audio too short as expected)")
        else:
            print(f"  ✓ Recording saved: {result}")

        return True

    except Exception as e:
        print(f"  ✗ Recording error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("SpeechMate Client Tests")
    print("=" * 50)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Audio Devices", test_audio_devices()))
    results.append(("Clipboard", test_clipboard()))
    results.append(("Configuration", test_config()))
    results.append(("API Client", test_api_client()))
    results.append(("Recording", test_recording()))

    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)

    passed = 0
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {name}: {status}")
        if result:
            passed += 1

    print(f"\nTotal: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
