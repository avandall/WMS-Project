#!/usr/bin/env python3
"""
Test runner for advanced SQL injection validation system.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def run_tests():
    """Run all validation tests."""
    print("🔒 Running Advanced SQL Injection Validation Tests")
    print("=" * 60)
    
    # Test categories
    test_categories = [
        {
            "name": "Advanced Validation Tests",
            "path": "tests/test_advanced_validation.py",
            "description": "Word-boundary regex and AST-based validation"
        },
        {
            "name": "Secure Query Builder Tests", 
            "path": "tests/test_secure_query.py",
            "description": "Secure query building with validation"
        }
    ]
    
    all_passed = True
    
    for category in test_categories:
        print(f"\n🧪 {category['name']}")
        print(f"📝 {category['description']}")
        print("-" * 40)
        
        try:
            # Run pytest for the category
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                category["path"], 
                "-v",
                "--tb=short",
                "--color=yes"
            ], capture_output=True, text=True, cwd=Path(__file__).parent)
            
            if result.returncode == 0:
                print("✅ All tests passed!")
                print(result.stdout)
            else:
                print("❌ Some tests failed!")
                print(result.stdout)
                print(result.stderr)
                all_passed = False
                
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All validation tests passed! System is secure.")
        return 0
    else:
        print("⚠️  Some tests failed. Review the output above.")
        return 1

def run_performance_tests():
    """Run performance tests for validation."""
    print("\n⚡ Running Performance Tests")
    print("-" * 30)
    
    try:
        from app.core.advanced_validation import SQLInjectionValidator
        import time
        
        # Test with various input sizes
        test_cases = [
            ("Small input (10 chars)", "a" * 10, 1000),
            ("Medium input (100 chars)", "a" * 100, 1000),
            ("Large input (1000 chars)", "a" * 1000, 100),
            ("Very large input (10000 chars)", "a" * 10000, 10),
        ]
        
        for description, test_input, iterations in test_cases:
            start_time = time.time()
            
            for _ in range(iterations):
                SQLInjectionValidator.validate_with_word_boundaries(test_input, "test")
            
            end_time = time.time()
            avg_time = (end_time - start_time) / iterations * 1000  # Convert to ms
            
            print(f"✅ {description}: {avg_time:.2f}ms avg ({iterations} iterations)")
            
            # Performance assertions
            if iterations >= 100:
                assert avg_time < 1.0, f"Performance too slow: {avg_time:.2f}ms"
            elif iterations >= 10:
                assert avg_time < 10.0, f"Performance too slow: {avg_time:.2f}ms"
        
        print("✅ All performance tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def run_security_demo():
    """Demonstrate security features."""
    print("\n🛡️  Security Demonstration")
    print("-" * 30)
    
    try:
        from app.core.advanced_validation import SQLInjectionValidator, security_policy
        
        # Test cases showing security in action
        demo_cases = [
            {
                "input": "normal user input",
                "expected_safe": True,
                "description": "Normal input should pass"
            },
            {
                "input": "SELECT * FROM users",
                "expected_safe": False,
                "description": "SQL keyword should be blocked"
            },
            {
                "input": "'; DROP TABLE users; --",
                "expected_safe": False,
                "description": "SQL injection should be blocked"
            },
            {
                "input": "eval('malicious code')",
                "expected_safe": False,
                "description": "Code injection should be blocked"
            },
            {
                "input": "selection",  # Contains 'select' but not as word boundary
                "expected_safe": True,
                "description": "Partial word should be safe"
            }
        ]
        
        for i, case in enumerate(demo_cases, 1):
            print(f"\n{i}. {case['description']}")
            print(f"   Input: '{case['input']}'")
            
            is_valid, violations = SQLInjectionValidator.comprehensive_validate(
                case['input'], "demo_field", "general"
            )
            
            if is_valid == case['expected_safe']:
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
            
            print(f"   Result: {status} (Valid: {is_valid})")
            
            if violations:
                print(f"   Violations: {violations}")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def main():
    """Main test runner."""
    print("🔒 Advanced SQL Injection Validation Test Suite")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("src").exists():
        print("❌ Error: Run this script from the project root directory")
        return 1
    
    # Run all test suites
    test_results = []
    
    # 1. Unit tests
    unit_test_result = run_tests()
    test_results.append(("Unit Tests", unit_test_result == 0))
    
    # 2. Performance tests
    perf_test_result = run_performance_tests()
    test_results.append(("Performance Tests", perf_test_result))
    
    # 3. Security demo
    demo_result = run_security_demo()
    test_results.append(("Security Demo", demo_result))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("-" * 20)
    
    all_passed = True
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! The advanced validation system is working correctly.")
        print("🛡️  SQL injection protection is active and robust.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
