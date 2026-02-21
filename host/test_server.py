#!/usr/bin/env python3
"""
SpeechMate Host Server Test Script
Tests basic functionality without starting the server
"""
import sys
from pathlib import Path

# Add host directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test all imports"""
    print("Testing imports...")

    try:
        from app.config import config, ASR_MODELS
        print("  ✓ app.config")
    except Exception as e:
        print(f"  ✗ app.config: {e}")
        return False

    try:
        from app.database import init_db, get_all_api_keys
        print("  ✓ app.database")
    except Exception as e:
        print(f"  ✗ app.database: {e}")
        return False

    try:
        from models.asr_model import get_asr_model
        print("  ✓ models.asr_model")
    except Exception as e:
        print(f"  ✗ models.asr_model: {e}")
        return False

    try:
        from models.translation_model import translate_text
        print("  ✓ models.translation_model")
    except Exception as e:
        print(f"  ✗ models.translation_model: {e}")
        return False

    return True


def test_database():
    """Test database operations"""
    print("\nTesting database...")

    try:
        from app.database import init_db, get_all_api_keys, create_api_key

        init_db()
        print("  ✓ Database initialized")

        keys = get_all_api_keys()
        print(f"  ✓ Found {len(keys)} API keys")

        return True
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        return False


def test_translation():
    """Test translation functionality"""
    print("\nTesting translation...")

    try:
        from models.translation_model import translate_text

        # Test with simple text
        text, time_taken = translate_text("你好", "zh", "en")
        print(f"  ✓ Translation: '你好' -> '{text}' ({time_taken:.2f}s)")

        return True
    except Exception as e:
        print(f"  ✗ Translation error: {e}")
        return False


def test_asr_model():
    """Test ASR model loading"""
    print("\nTesting ASR model (this may take a while)...")

    try:
        from models.asr_model import get_asr_model

        # Load the smallest model for testing
        model = get_asr_model("tiny", "cpu", "int8")
        print("  ✓ ASR model loaded (tiny)")

        return True
    except Exception as e:
        print(f"  ✗ ASR model error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("SpeechMate Host Server Tests")
    print("=" * 50)

    results = []

    results.append(("Imports", test_imports()))
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
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
