"""
Comprehensive Test Runner - Run all test categories
Runs: unit, integration, api, performance, security, regression, e2e
Usage: python tests/run_all_tests.py [category]
Categories: unit, integration, api, performance, security, regression, e2e, all
"""

import sys
import os
import subprocess
import time
from pathlib import Path


def run_test_category(category, test_path):
    """Run tests for a specific category"""
    print(f"\n{'='*60}")
    print(f"Running {category.upper()} Tests")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Run pytest for the category
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            test_path, 
            "-v",
            "--tb=short"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n{category.upper()} Tests Results:")
        print(f"Duration: {duration:.2f}s")
        print(f"Exit Code: {result.returncode}")
        
        if result.stdout:
            print(f"Output:\n{result.stdout}")
        
        if result.stderr:
            print(f"Errors:\n{result.stderr}")
        
        # Count passed/failed from pytest output
        if result.stdout:
            lines = result.stdout.split('\n')
            passed = sum(1 for line in lines if 'PASSED' in line)
            failed = sum(1 for line in lines if 'FAILED' in line)
            total = passed + failed
            
            if total > 0:
                success_rate = (passed / total) * 100
                print(f"Summary: {passed} passed, {failed} failed, {total} total ({success_rate:.1f}%)")
            else:
                print("Summary: No tests found")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running {category} tests: {e}")
        return False


def main():
    """Main test runner"""
    
    # Define test categories and their paths
    test_categories = {
        "unit": {
            "path": "unit/",
            "description": "Unit Tests - Run continuously with code changes"
        },
        "integration": {
            "path": "integration/test_working_integration.py",
            "description": "Integration Tests - Working functionality tests"
        },
        "api": {
            "path": "api/",
            "description": "API Tests - Run before code merge"
        },
        "performance": {
            "path": "performance/",
            "description": "Performance Tests - High performance with proper tools"
        },
        "security": {
            "path": "security/",
            "description": "Security Tests - SQL injection, RBAC, JWT validation"
        },
        "regression": {
            "path": "regression/",
            "description": "Regression Tests - Critical paths and bug fixes"
        },
        "e2e": {
            "path": "e2e/total_project_test.py",
            "description": "E2E Tests - Complete end-to-end user workflows"
        }
    }
    
    # Get command line arguments
    args = sys.argv[1:]
    
    if not args:
        print("Comprehensive Test Runner")
        print("=" * 50)
        print("Usage: python tests/run_all_tests.py [category]")
        print("\nAvailable categories:")
        for category, info in test_categories.items():
            print(f"  {category:12} - {info['description']}")
        print("\nExamples:")
        print("  python tests/run_all_tests.py unit")
        print("  python tests/run_all_tests.py integration")
        print("  python tests/run_all_tests.py api")
        print("  python tests/run_all_tests.py performance")
        print("  python tests/run_all_tests.py security")
        print("  python tests/run_all_tests.py regression")
        print("  python tests/run_all_tests.py e2e")
        print("  python tests/run_all_tests.py all")
        print("=" * 50)
        return
    
    # Handle specific category or 'all'
    if args[0].lower() == "all":
        print("Running ALL test categories...")
        print("=" * 50)
        
        results = {}
        for category, info in test_categories.items():
            success = run_test_category(category, info["path"])
            results[category] = success
        
        print("\n" + "=" * 50)
        print("OVERALL SUMMARY")
        print("=" * 50)
        
        passed_categories = sum(1 for success in results.values() if success)
        total_categories = len(results)
        
        for category, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{category:12} Tests: {status}")
        
        print(f"\nOverall: {passed_categories}/{total_categories} categories passed")
        
        if passed_categories == total_categories:
            print("🎉 ALL TEST CATEGORIES PASSED!")
        else:
            print(f"⚠️  {total_categories - passed_categories} categories failed")
        
        print("=" * 50)
        
    else:
        category = args[0].lower()
        if category in test_categories:
            success = run_test_category(category, test_categories[category]["path"])
            
            if success:
                print(f"\n🎉 {category.upper()} tests completed successfully!")
            else:
                print(f"\n❌ {category.upper()} tests failed!")
        else:
            print(f"❌ Unknown category: {category}")
            print(f"Available categories: {', '.join(test_categories.keys())}")


if __name__ == "__main__":
    main()
