#!/usr/bin/env python3
"""
SpeechMate Test Runner Script

Usage:
    python run_tests.py              # Run unit tests only
    python run_tests.py --all         # Run all tests including slow
    python run_tests.py --coverage    # Run with coverage report
    python run_tests.py --client      # Run client tests
"""
import subprocess
import sys
import argparse
from pathlib import Path


def run_host_unit_tests():
    """Run host unit tests (excluding slow tests)"""
    print("=" * 60)
    print("Running Host Unit Tests...")
    print("=" * 60)
    result = subprocess.run(
        ["pytest", "tests/", "-v", "-m", "not slow", "--tb=short"],
        cwd=Path(__file__).parent.parent / "host"
    )
    return result.returncode == 0


def run_host_all_tests():
    """Run all host tests including slow tests"""
    print("=" * 60)
    print("Running All Host Tests (including slow)...")
    print("=" * 60)
    result = subprocess.run(
        ["pytest", "tests/", "-v", "--tb=short"],
        cwd=Path(__file__).parent.parent / "host"
    )
    return result.returncode == 0


def run_host_tests_with_coverage():
    """Run host tests with coverage report"""
    print("=" * 60)
    print("Running Host Tests with Coverage...")
    print("=" * 60)
    result = subprocess.run(
        ["pytest", "tests/", "-v", "-m", "not slow",
         "--cov=app", "--cov=models", "--cov-report=html", "--cov-report=term"],
        cwd=Path(__file__).parent.parent / "host"
    )
    return result.returncode == 0


def run_client_tests():
    """Run client tests"""
    print("=" * 60)
    print("Running Client Tests...")
    print("=" * 60)
    result = subprocess.run(
        ["pytest", "tests/", "-v", "--tb=short"],
        cwd=Path(__file__).parent.parent / "client"
    )
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="SpeechMate Test Runner")
    parser.add_argument("--all", action="store_true", help="Run all tests including slow")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--client", action="store_true", help="Run client tests")
    parser.add_argument("--host", action="store_true", help="Run host tests only")

    args = parser.parse_args()

    success = True

    if args.client:
        success = run_client_tests() and success
    elif args.host:
        if args.coverage:
            success = run_host_tests_with_coverage() and success
        elif args.all:
            success = run_host_all_tests() and success
        else:
            success = run_host_unit_tests() and success
    else:
        # Default: run both host and client tests
        if args.coverage:
            success = run_host_tests_with_coverage() and success
        elif args.all:
            success = run_host_all_tests() and success
        else:
            success = run_host_unit_tests() and success
        success = run_client_tests() and success

    if success:
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Some tests failed!")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
