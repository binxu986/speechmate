#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SpeechMate Host Server Test Script
Tests basic functionality without starting the server

Run with: python test_server.py
Or with pytest: pytest tests/ -v
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
        from models.asr_model import get_asr_model, transcribe_audio, get_audio_duration, unload_model
        print("  [OK] models.asr_model")
    except Exception as e:
        print(f"  [FAIL] models.asr_model: {e}")
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


def test_asr_model_loading():
    """Test ASR model loading"""
    print("\nTesting ASR model (this may take a while on first run)...")

    try:
        from models.asr_model import get_asr_model, unload_model, get_model_info

        # Load the smallest model for testing
        model = get_asr_model("tiny", "cpu", "int8")
        print("  [OK] ASR model loaded (tiny)")

        info = get_model_info()
        print(f"  [OK] Model info: {info}")

        # Unload model
        unload_model()
        print("  [OK] Model unloaded")

        return True
    except Exception as e:
        print(f"  [FAIL] ASR model error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoints():
    """Test API endpoint imports"""
    print("\nTesting API endpoints...")

    try:
        from app.main import app
        print("  [OK] FastAPI app imported")

        # Check routes
        routes = [route.path for route in app.routes]
        print(f"  [OK] Routes: {routes}")

        return True
    except Exception as e:
        print(f"  [FAIL] API error: {e}")
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
    results.append(("API Endpoints", test_api_endpoints()))

    # Ask before loading model (requires download)
    print("\n" + "-" * 50)
    response = input("Test ASR model loading? (requires download, y/n): ").strip().lower()
    if response == 'y':
        results.append(("ASR Model", test_asr_model_loading()))
    else:
        print("Skipping ASR model test")

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