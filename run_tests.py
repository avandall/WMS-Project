#!/usr/bin/env python3
"""
WMS Test Runner - Easy test execution script
Solves pytest I/O issues and provides convenient test running options.
"""

import sys
import subprocess
import argparse
from pathlib import Path

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
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--sql", action="store_true", help="Run SQL tests only")
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests only")
    parser.add_argument("--security", action="store_true", help="Run security tests only")
    parser.add_argument("--ai", action="store_true", help="Run AI tests only")
    parser.add_argument("--fast", action="store_true", help="Run fast tests only (unit + smoke)")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    
    args = parser.parse_args()
    
    # Default to all tests if no specific option given
    if not any([args.unit, args.sql, args.smoke, args.security, args.ai, args.fast]):
        args.all = True
    
    # Base pytest command
    pytest_cmd = ["python", "-m", "pytest"]
    
    # Add options
    if args.verbose:
        pytest_cmd.append("-v")
    if args.parallel:
        pytest_cmd.extend(["-n", "auto"])
    if args.coverage:
        pytest_cmd.extend(["--cov=src", "--cov-report=term-missing"])
    
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
