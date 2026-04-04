#!/usr/bin/env python3
"""
WMS Test Runner - Easy test execution script
Solves pytest I/O issues and provides convenient test running options.
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path

def load_test_env():
    """Load test environment variables."""
    env_file = Path(".env.test")
    if env_file.exists():
        print(f"🔧 Loading test environment from {env_file}")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value
    else:
        print("⚠️  No .env.test file found, using default test values")
        os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
        os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")

def run_command(cmd, description):
    """Run a command and handle results."""
    print(f"\n🧪 {description}")
    print(f"📝 Command: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr and result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="WMS Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--sql", action="store_true", help="Run SQL tests")
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests")
    parser.add_argument("--security", action="store_true", help="Run security tests")
    parser.add_argument("--ai", action="store_true", help="Run AI tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--fast", action="store_true", help="Run fast tests (unit + smoke)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Load test environment first
    load_test_env()
    
    results = []
    
    # Determine which tests to run
    if args.all:
        args.unit = args.sql = args.smoke = args.security = args.ai = True
    
    if args.fast:
        args.unit = args.smoke = True
    
    # If no arguments specified, run all tests
    if not any([args.unit, args.sql, args.smoke, args.security, args.ai]):
        args.unit = args.sql = args.smoke = args.security = args.ai = True
    
    # Base pytest command
    pytest_cmd = ["python", "-m", "pytest"]
    
    # Add options
    if args.verbose:
        pytest_cmd.append("-v")
    
    # Test suites to run
    test_suites = []
    
    if args.all or args.unit:
        test_suites.append(("tests/unit/", "Unit Tests"))
    
    if args.all or args.sql:
        test_suites.append(("tests/sql/", "SQL Tests"))
    
    if args.all or args.smoke or args.fast:
        test_suites.append(("tests/test_smoke.py", "Smoke Tests"))
    
    if args.all or args.security:
        test_suites.append(("tests/test_sql_exec.py", "SQL Security Tests"))
        test_suites.append(("tests/test_sql_parser.py", "SQL Parser Tests"))
    
    if args.all or args.ai:
        test_suites.append(("tests/test_sql_parser.py", "AI Parser Tests"))
    
    # Fast mode: only unit + smoke tests
    if args.fast:
        test_suites = [
            ("tests/unit/", "Unit Tests"),
            ("tests/test_smoke.py", "Smoke Tests")
        ]
    
    # Run test suites
    results = []
    for test_path, description in test_suites:
        cmd = pytest_cmd + [test_path]
        success = run_command(cmd, description)
        results.append((description, success))
    
    # Run additional tests
    if args.all or args.security:
        print("\n🔒 Running SQL Security Tests...")
        success = run_command(["python", "run_sql_exec_tests.py"], "SQL Security Tests")
        results.append(("SQL Security Tests", success))
    
    if args.all or args.ai:
        print("\n🤖 Running AI Relevance Filter Tests...")
        success = run_command(["python", "test_relevance_filter.py"], "AI Relevance Filter Tests")
        results.append(("AI Relevance Filter Tests", success))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status:<12} {description}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"📈 Total: {len(results)} suites")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Great job!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {failed} test suite(s) failed. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
