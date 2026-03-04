#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SpeechMate Test Runner Script

Usage:
    python run_tests.py              # Run unit tests only
    python run_tests.py --all         # Run all tests including slow
    python run_tests.py --coverage    # Run with coverage report
    python run_tests.py --report      # Generate test report
"""
import subprocess
import sys
import argparse
import io
import re
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def parse_test_output(output: str) -> dict:
    """Parse pytest output to extract test results"""
    result = {
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'deselected': 0,
        'warnings': 0,
        'total': 0,
        'duration': '',
        'failed_tests': []
    }

    # Parse summary line (e.g., "5 passed, 2 failed, 3 skipped")
    summary_match = re.search(r'(\d+) passed', output)
    if summary_match:
        result['passed'] = int(summary_match.group(1))

    summary_match = re.search(r'(\d+) failed', output)
    if summary_match:
        result['failed'] = int(summary_match.group(1))

    summary_match = re.search(r'(\d+) skipped', output)
    if summary_match:
        result['skipped'] = int(summary_match.group(1))

    summary_match = re.search(r'(\d+) deselected', output)
    if summary_match:
        result['deselected'] = int(summary_match.group(1))

    summary_match = re.search(r'(\d+) warnings?', output)
    if summary_match:
        result['warnings'] = int(summary_match.group(1))

    result['total'] = result['passed'] + result['failed'] + result['skipped']

    # Extract failed test names
    failed_matches = re.findall(r'FAILED (.*?)::', output)
    result['failed_tests'] = failed_matches

    return result


def run_tests_with_capture(cwd: Path, args: list) -> tuple:
    """Run tests and capture output"""
    result = subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.returncode == 0, result.stdout + result.stderr


def run_host_unit_tests(report_mode=False):
    """Run host unit tests (excluding slow tests)"""
    print("=" * 60)
    print("Running Host Unit Tests...")
    print("=" * 60)

    if report_mode:
        success, output = run_tests_with_capture(
            Path(__file__).parent.parent / "host",
            ["pytest", "tests/", "-v", "-m", "not slow", "--tb=short"]
        )
        return success, parse_test_output(output)
    else:
        result = subprocess.run(
            ["pytest", "tests/", "-v", "-m", "not slow", "--tb=short"],
            cwd=Path(__file__).parent.parent / "host"
        )
        return result.returncode == 0, None


def run_host_all_tests(report_mode=False):
    """Run all host tests including slow tests"""
    print("=" * 60)
    print("Running All Host Tests (including slow)...")
    print("=" * 60)

    if report_mode:
        success, output = run_tests_with_capture(
            Path(__file__).parent.parent / "host",
            ["pytest", "tests/", "-v", "--tb=short"]
        )
        return success, parse_test_output(output)
    else:
        result = subprocess.run(
            ["pytest", "tests/", "-v", "--tb=short"],
            cwd=Path(__file__).parent.parent / "host"
        )
        return result.returncode == 0, None


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
    return result.returncode == 0, None


def run_client_tests(report_mode=False):
    """Run client tests"""
    print("=" * 60)
    print("Running Client Tests...")
    print("=" * 60)

    if report_mode:
        success, output = run_tests_with_capture(
            Path(__file__).parent.parent / "client",
            ["pytest", "tests/", "-v", "--tb=short"]
        )
        return success, parse_test_output(output)
    else:
        result = subprocess.run(
            ["pytest", "tests/", "-v", "--tb=short"],
            cwd=Path(__file__).parent.parent / "client"
        )
        return result.returncode == 0, None


def generate_report(host_result: dict, client_result: dict, all_tests: bool = False) -> str:
    """Generate markdown test report"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# SpeechMate Test Report

Generated: {now}

## Summary

| Component | Passed | Failed | Skipped | Total | Status |
|-----------|--------|--------|---------|-------|--------|
| Host      | {host_result['passed']} | {host_result['failed']} | {host_result['skipped']} | {host_result['total']} | {'PASS' if host_result['failed'] == 0 else 'FAIL'} |
| Client    | {client_result['passed']} | {client_result['failed']} | {client_result['skipped']} | {client_result['total']} | {'PASS' if client_result['failed'] == 0 else 'FAIL'} |
| **Total** | **{host_result['passed'] + client_result['passed']}** | **{host_result['failed'] + client_result['failed']}** | **{host_result['skipped'] + client_result['skipped']}** | **{host_result['total'] + client_result['total']}** | **{'PASS' if host_result['failed'] + client_result['failed'] == 0 else 'FAIL'}** |

## Test Mode

- Mode: {'All tests (including slow)' if all_tests else 'Unit tests only (excluding slow)'}

## Host Tests

- Passed: {host_result['passed']}
- Failed: {host_result['failed']}
- Skipped: {host_result['skipped']}
- Deselected: {host_result['deselected']}
- Warnings: {host_result['warnings']}

"""

    if host_result['failed_tests']:
        report += "### Failed Host Tests\n\n"
        for test in host_result['failed_tests']:
            report += f"- {test}\n"
        report += "\n"

    report += f"""## Client Tests

- Passed: {client_result['passed']}
- Failed: {client_result['failed']}
- Skipped: {client_result['skipped']}
- Warnings: {client_result['warnings']}

"""

    if client_result['failed_tests']:
        report += "### Failed Client Tests\n\n"
        for test in client_result['failed_tests']:
            report += f"- {test}\n"
        report += "\n"

    # Overall result
    total_failed = host_result['failed'] + client_result['failed']
    if total_failed == 0:
        report += "## Result: ALL TESTS PASSED\n"
    else:
        report += f"## Result: {total_failed} TEST(S) FAILED\n"

    return report


def main():
    parser = argparse.ArgumentParser(description="SpeechMate Test Runner")
    parser.add_argument("--all", action="store_true", help="Run all tests including slow")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--client", action="store_true", help="Run client tests only")
    parser.add_argument("--host", action="store_true", help="Run host tests only")
    parser.add_argument("--report", action="store_true", help="Generate test report file")

    args = parser.parse_args()

    success = True
    host_result = None
    client_result = None

    report_mode = args.report

    if args.client:
        success, client_result = run_client_tests(report_mode)
    elif args.host:
        if args.coverage:
            success, _ = run_host_tests_with_coverage()
        elif args.all:
            success, host_result = run_host_all_tests(report_mode)
        else:
            success, host_result = run_host_unit_tests(report_mode)
    else:
        # Default: run both host and client tests
        if args.coverage:
            success, _ = run_host_tests_with_coverage()
        elif args.all:
            success, host_result = run_host_all_tests(report_mode)
        else:
            success, host_result = run_host_unit_tests(report_mode)
        client_success, client_result = run_client_tests(report_mode)
        success = success and client_success

    # Generate report if requested
    if report_mode and host_result and client_result:
        report = generate_report(host_result, client_result, args.all)
        report_dir = Path(__file__).parent.parent / "test_reports"
        report_dir.mkdir(exist_ok=True)
        report_file = report_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_file.write_text(report, encoding='utf-8')
        print(f"\nTest report saved to: {report_file}")

    if success:
        print("\n" + "=" * 60)
        print("[PASS] All tests passed!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("[FAIL] Some tests failed!")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
