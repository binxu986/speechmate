#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SpeechMate Host Server Test Script
Tests basic functionality without starting the server
"""
import sys
import os
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add host directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test all imports"""
    print("Testing imports...")

    try:
        from app.config import config, ASR_MODELS
        print("  [OK] app.config")
    except Exception as e:
        print(f"  [FAIL] app.config: {e}")
        return False

    try:
        from app.database import init_db, get_all_api_keys
        print("  [OK] app.database")
    except Exception as e:
        print(f"  [FAIL] app.database: {e}")
        return False

    try:
        from models.asr_model import get_asr_model
        print("  [OK] models.asr_model")
    except Exception as e:
        print(f"  [FAIL] models.asr_model: {e}")
        return False

    try:
        from models.translation_model import translate_text
        print("  [OK] models.translation_model")
    except Exception as e:
        print(f"  [FAIL] models.translation_model: {e}")
        return False

    return True


def test_database():
    """Test database operations"""
    print("\nTesting database...")

    try:
        from app.database import init_db, get_all_api_keys, create_api_key

        init_db()
        print("  [OK] Database initialized")

        keys = get_all_api_keys()
        print(f"  [OK] Found {len(keys)} API keys")

        return True
    except Exception as e:
        print(f"  [FAIL] Database error: {e}")
        return False


def test_translation():
    """Test translation functionality"""
    print("\nTesting translation...")

    try:
        from models.translation_model import translate_text

        # Test with simple text
        text, time_taken = translate_text("Hello", "en", "zh")
        print(f"  [OK] Translation: 'Hello' -> '{text}' ({time_taken:.2f}s)")

        return True
    except Exception as e:
        print(f"  [FAIL] Translation error: {e}")
        return False


def test_asr_model():
    """Test ASR model loading"""
    print("\nTesting ASR model (this may take a while)...")

    try:
        from models.asr_model import get_asr_model

        # Load the smallest model for testing
        model = get_asr_model("tiny", "cpu", "int8")
        print("  [OK] ASR model loaded (tiny)")

        return True
    except Exception as e:
        print(f"  [FAIL] ASR model error: {e}")
        return False


def test_config():
    """Test configuration"""
    print("\nTesting configuration...")

    try:
        from app.config import config, detect_gpu

        device, compute_type = detect_gpu()
        print(f"  [OK] Detected device: {device}, compute_type: {compute_type}")
        print(f"  [OK] Current config - model: {config.model.asr_model}, device: {config.model.asr_device}")

        return True
    except Exception as e:
        print(f"  [FAIL] Config error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("SpeechMate Host Server Tests")
    print("=" * 50)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Config", test_config()))
    results.append(("Database", test_database()))
    results.append(("Translation", test_translation()))
    results.append(("ASR Model", test_asr_model()))

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
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print("\n[FAILED] Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
