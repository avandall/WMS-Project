#!/usr/bin/env python3
"""
Test runner for enhanced AI chains with SQL extraction and logging.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def run_enhanced_chains_tests():
    """Run all enhanced chains tests."""
    print("🤖 Running Enhanced AI Chains Tests")
    print("=" * 60)
    
    # Test categories
    test_categories = [
        {
            "name": "SQL Extraction Tests",
            "path": "tests/test_enhanced_chains.py::TestSQLExtractor",
            "description": "Hardened SQL extraction with multiple LLM formats"
        },
        {
            "name": "Enhanced AI Chains Tests",
            "path": "tests/test_enhanced_chains.py::TestEnhancedAIChains",
            "description": "Enhanced chains with logging and metrics"
        },
        {
            "name": "Backward Compatibility Tests",
            "path": "tests/test_enhanced_chains.py::TestBackwardCompatibility",
            "description": "Backward compatibility for existing functions"
        },
        {
            "name": "Integration Tests",
            "path": "tests/test_enhanced_chains.py::TestIntegration",
            "description": "End-to-end integration tests"
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
        print("🎉 All enhanced chains tests passed! System is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Review the output above.")
        return 1

def run_sql_extraction_demo():
    """Demonstrate SQL extraction capabilities."""
    print("\n🔍 SQL Extraction Demonstration")
    print("-" * 30)
    
    try:
        from app.infrastructure.ai.enhanced_chains import SQLExtractor
        
        # Test cases showing different LLM output formats
        demo_cases = [
            {
                "name": "Standard Markdown SQL",
                "input": "```sql\nSELECT * FROM products WHERE price > 100\n```",
                "expected": "SELECT * FROM products WHERE price > 100"
            },
            {
                "name": "PostgreSQL Block",
                "input": "```postgresql\nSELECT id, name FROM users\n```",
                "expected": "SELECT id, name FROM users"
            },
            {
                "name": "Generic Code Block",
                "input": "```\nWITH cte AS (SELECT * FROM orders) SELECT * FROM cte\n```",
                "expected": "WITH cte AS (SELECT * FROM orders) SELECT * FROM cte"
            },
            {
                "name": "Text Marker",
                "input": "SQL:\nSELECT COUNT(*) FROM customers",
                "expected": "SELECT COUNT(*) FROM customers"
            },
            {
                "name": "Inline Backticks",
                "input": "Use this query: `SELECT name FROM products` to get product names",
                "expected": "SELECT name FROM products"
            },
            {
                "name": "Complex CTE with Comments",
                "input": "```sql\n-- Get top products\nWITH ranked_products AS (\n  SELECT *, ROW_NUMBER() OVER (ORDER BY price DESC) as rn\n  FROM products\n  WHERE active = true\n)\nSELECT * FROM ranked_products WHERE rn <= 10\n```",
                "expected": "WITH ranked_products AS (\n  SELECT *, ROW_NUMBER() OVER (ORDER BY price DESC) as rn\n  FROM products\n  WHERE active = true\n)\nSELECT * FROM ranked_products WHERE rn <= 10"
            }
        ]
        
        for i, case in enumerate(demo_cases, 1):
            print(f"\n{i}. {case['name']}")
            print(f"   Input: {case['input'][:50]}...")
            
            result, issues = SQLExtractor.extract_sql(case['input'])
            
            if result == case['expected']:
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
            
            print(f"   Expected: {case['expected']}")
            print(f"   Got:      {result}")
            print(f"   Result:   {status}")
            
            if issues:
                print(f"   Issues:   {issues}")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def run_logging_demo():
    """Demonstrate structured logging capabilities."""
    print("\n📊 Structured Logging Demonstration")
    print("-" * 35)
    
    try:
        from app.infrastructure.ai.enhanced_chains import EnhancedAIChains
        import logging
        
        # Set up logging to see structured output
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        
        print("Creating EnhancedAIChains instance...")
        chains = EnhancedAIChains()
        
        print("Adding sample metrics...")
        # Add some sample metrics
        from app.infrastructure.ai.enhanced_chains import SQLGenerationMetrics
        
        sample_metrics = [
            SQLGenerationMetrics(
                question_length=25, sql_length=35, generation_time_ms=150.5,
                execution_time_ms=120.3, row_count=8, validation_violations=[],
                success=True
            ),
            SQLGenerationMetrics(
                question_length=30, sql_length=0, generation_time_ms=200.0,
                execution_time_ms=0, row_count=0, validation_violations=["Validation error"],
                success=False, error_type="Validation", error_message="SQL contains forbidden keywords"
            ),
            SQLGenerationMetrics(
                question_length=20, sql_length=40, generation_time_ms=180.2,
                execution_time_ms=95.7, row_count=15, validation_violations=[],
                success=True
            )
        ]
        
        for metric in sample_metrics:
            chains.metrics_history.append(metric)
        
        print("Generating performance metrics...")
        perf_metrics = chains.get_performance_metrics()
        
        print("\n📈 Performance Metrics:")
        print(f"   Total Requests: {perf_metrics['total_requests']}")
        print(f"   Successful: {perf_metrics['successful_requests']}")
        print(f"   Failed: {perf_metrics['failed_requests']}")
        print(f"   Success Rate: {perf_metrics['success_rate']:.1f}%")
        print(f"   Avg Generation Time: {perf_metrics['avg_generation_time_ms']:.1f}ms")
        print(f"   Avg SQL Length: {perf_metrics['avg_sql_length']:.1f}")
        print(f"   Avg Row Count: {perf_metrics['avg_row_count']:.1f}")
        
        if perf_metrics.get('common_errors'):
            print(f"   Common Errors: {perf_metrics['common_errors']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Logging demo failed: {e}")
        return False

def main():
    """Main test runner."""
    print("🤖 Enhanced AI Chains Test Suite")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("src").exists():
        print("❌ Error: Run this script from the project root directory")
        return 1
    
    # Run all test suites
    test_results = []
    
    # 1. Unit tests
    unit_test_result = run_enhanced_chains_tests()
    test_results.append(("Unit Tests", unit_test_result == 0))
    
    # 2. SQL extraction demo
    extraction_demo_result = run_sql_extraction_demo()
    test_results.append(("SQL Extraction Demo", extraction_demo_result))
    
    # 3. Logging demo
    logging_demo_result = run_logging_demo()
    test_results.append(("Logging Demo", logging_demo_result))
    
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
        print("🎉 All tests passed! The enhanced AI chains system is working correctly.")
        print("🤖 LLM SQL extraction, logging, and metrics are fully functional.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
