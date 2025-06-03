#!/usr/bin/env python3
"""
Test runner for the Claude Code Execution Teams Bot
Runs all test suites and generates a report
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path


def run_python_tests():
    """Run Python unit tests"""
    print("\n" + "="*60)
    print("Running Python Unit Tests")
    print("="*60)
    
    cmd = [sys.executable, "-m", "pytest", "tests/unit/", "-v", "--tb=short"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0


def run_ui_tests():
    """Run Puppeteer UI tests"""
    print("\n" + "="*60)
    print("Running UI Tests (Puppeteer)")
    print("="*60)
    
    # Check if node_modules exists
    if not Path("node_modules").exists():
        print("Installing Node dependencies...")
        subprocess.run(["npm", "install"], check=True)
    
    cmd = ["npm", "test"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0


def check_environment():
    """Check if required environment variables are set"""
    print("\n" + "="*60)
    print("Environment Check")
    print("="*60)
    
    required_vars = [
        "ANTHROPIC_API_KEY",
        "MicrosoftAppId",
        "MicrosoftAppPassword"
    ]
    
    all_set = True
    for var in required_vars:
        if os.environ.get(var):
            print(f"✓ {var}: Set")
        else:
            print(f"✗ {var}: Not set")
            all_set = False
    
    return all_set


def lint_code():
    """Run code linting"""
    print("\n" + "="*60)
    print("Code Linting")
    print("="*60)
    
    # Check if flake8 is installed
    try:
        import flake8
        cmd = ["flake8", "src/", "--max-line-length=100", "--ignore=E501,W503"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except ImportError:
        print("flake8 not installed, skipping linting")
        return True


def generate_report(results):
    """Generate test report"""
    report_path = "test_report.json"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results.values() if r),
            "failed": sum(1 for r in results.values() if not r)
        }
    }
    
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nTest report saved to {report_path}")
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {report['summary']['total']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    
    return report['summary']['failed'] == 0


def main():
    """Main test runner"""
    print("Claude Code Execution Teams Bot - Test Suite")
    print("Version: 1.0.0")
    
    results = {}
    
    # Run tests
    results["Environment"] = check_environment()
    results["Linting"] = lint_code()
    results["Python Tests"] = run_python_tests()
    
    # UI tests are optional if running in CI without display
    if os.environ.get("DISPLAY") or os.environ.get("CI") != "true":
        results["UI Tests"] = run_ui_tests()
    else:
        print("\nSkipping UI tests (no display available)")
    
    # Generate report
    all_passed = generate_report(results)
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()