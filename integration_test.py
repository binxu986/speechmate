#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SpeechMate Integration Test Script
Runs full integration tests with the server running
"""
import sys
import os
import time
import subprocess
import signal
import tempfile
import wave
import numpy as np
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Configure HuggingFace mirror
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

BASE_DIR = Path(__file__).parent
HOST_DIR = BASE_DIR / "host"
TEST_ITERATIONS = 10


def create_test_audio(duration=2.0, sample_rate=16000):
    """Create a simple test audio file (sine wave)"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Create a 440Hz sine wave
    audio = np.sin(440 * 2 * np.pi * t) * 0.5
    # Convert to 16-bit PCM
    audio = (audio * 32767).astype(np.int16)

    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_path = temp_file.name
    temp_file.close()

    with wave.open(temp_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())

    return temp_path


def test_health_check(base_url):
    """Test server health endpoint"""
    import requests
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def test_transcribe_api(base_url, api_key, audio_path):
    """Test transcribe API"""
    import requests
    try:
        with open(audio_path, "rb") as f:
            files = {"audio": ("test.wav", f, "audio/wav")}
            headers = {"X-API-Key": api_key}
            response = requests.post(
                f"{base_url}/api/v1/transcribe",
                files=files,
                headers=headers,
                timeout=60
            )
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, {"error": str(e)}


def test_translate_api(base_url, api_key, audio_path, source="zh", target="en"):
    """Test translate API"""
    import requests
    try:
        with open(audio_path, "rb") as f:
            files = {"audio": ("test.wav", f, "audio/wav")}
            data = {"source_lang": source, "target_lang": target}
            headers = {"X-API-Key": api_key}
            response = requests.post(
                f"{base_url}/api/v1/translate",
                files=files,
                data=data,
                headers=headers,
                timeout=60
            )
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, {"error": str(e)}


def run_single_test(iteration, base_url, api_key, audio_path):
    """Run a single test iteration"""
    print(f"\n--- Test Iteration {iteration} ---")

    results = {
        "health": False,
        "transcribe": False,
        "translate": False
    }

    # Test health check
    print("  Testing health check...")
    results["health"] = test_health_check(base_url)
    print(f"    Health check: {'PASS' if results['health'] else 'FAIL'}")

    # Test transcribe
    print("  Testing transcribe API...")
    success, response = test_transcribe_api(base_url, api_key, audio_path)
    results["transcribe"] = success
    if success:
        print(f"    Transcribe: PASS (text: '{response.get('text', '')[:30]}...')")
    else:
        print(f"    Transcribe: FAIL ({response.get('error', 'Unknown error')})")

    # Test translate
    print("  Testing translate API...")
    success, response = test_translate_api(base_url, api_key, audio_path, "zh", "en")
    results["translate"] = success
    if success:
        orig = response.get('original_text', '')[:20]
        trans = response.get('translated_text', '')[:20]
        print(f"    Translate: PASS ('{orig}...' -> '{trans}...')")
    else:
        print(f"    Translate: FAIL ({response.get('error', 'Unknown error')})")

    return all(results.values())


def main():
    """Main test runner"""
    print("=" * 60)
    print("SpeechMate Integration Tests")
    print(f"Running {TEST_ITERATIONS} iterations")
    print("=" * 60)

    base_url = "http://localhost:8000"
    api_key = os.environ.get("TEST_API_KEY", "")

    # Create test audio
    print("\nCreating test audio file...")
    audio_path = create_test_audio(duration=2.0)
    print(f"  Created: {audio_path}")

    # Check server status
    print(f"\nChecking server at {base_url}...")
    if not test_health_check(base_url):
        print("  [ERROR] Server is not running!")
        print("  Please start the server first:")
        print(f"    cd {HOST_DIR}")
        print("    python start_server.py")
        return 1
    print("  [OK] Server is running")

    # Get API key from server info if not provided
    if not api_key:
        try:
            import requests
            # Get the actual API key from database
            response = requests.get(f"{base_url}/api/v1/info", timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Note: admin_api_key is for admin operations, need actual API key
                # For testing, we'll get it from a separate endpoint
                print("  [INFO] Getting API key from server...")
        except:
            pass

    # Get actual API key from database via a test request
    if not api_key:
        try:
            # First try with admin key to list API keys
            response = requests.get(f"{base_url}/api/v1/info", timeout=5)
            if response.status_code == 200:
                admin_key = response.json().get("admin_api_key", "")
                response = requests.get(
                    f"{base_url}/api/v1/api-keys",
                    headers={"X-API-Key": admin_key},
                    timeout=5
                )
                if response.status_code == 200:
                    keys = response.json().get("api_keys", [])
                    if keys:
                        api_key = keys[0]["key"]
                        print(f"  [OK] Using API key: {api_key[:8]}...")
        except Exception as e:
            print(f"  [WARN] Could not get API key: {e}")

    if not api_key:
        print("  [ERROR] Could not get API key")
        return 1

    # Run tests
    passed = 0
    failed = 0
    start_time = time.time()

    for i in range(1, TEST_ITERATIONS + 1):
        success = run_single_test(i, base_url, api_key, audio_path)
        if success:
            passed += 1
        else:
            failed += 1

    total_time = time.time() - start_time

    # Clean up
    try:
        os.unlink(audio_path)
    except:
        pass

    # Print results
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"  Total iterations: {TEST_ITERATIONS}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Success rate: {passed/TEST_ITERATIONS*100:.1f}%")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Average time per iteration: {total_time/TEST_ITERATIONS:.2f}s")

    if failed == 0:
        print("\n[SUCCESS] All integration tests passed!")
        return 0
    else:
        print(f"\n[FAILED] {failed} iterations failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
