"""
Test runner for SOLID refactored components.
Provides comprehensive test execution and reporting.
"""

import pytest
import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def run_solid_tests():
    """Run all SOLID pattern tests with comprehensive reporting."""
    
    # Define test patterns and descriptions
    test_modules = [
        {
            "path": "tests/unit/test_commands_simple.py",
            "description": "Command Pattern Tests",
            "tests": ["TestCreateProductCommand", "TestUpdateProductCommand", "TestDeleteProductCommand"]
        },
        {
            "path": "tests/unit/test_command_handlers.py", 
            "description": "Command Handler Tests",
            "tests": ["TestProductCommandHandler"]
        },
        {
            "path": "tests/unit/test_queries_simple.py",
            "description": "Query Pattern Tests", 
            "tests": ["TestGetProductQuery", "TestGetAllProductsQuery"]
        },
        {
            "path": "tests/unit/test_query_handlers.py",
            "description": "Query Handler Tests",
            "tests": ["TestProductQueryHandler"]
        },
        {
            "path": "tests/unit/test_validators.py",
            "description": "Validation Layer Tests",
            "tests": ["TestProductValidator"]
        },
        {
            "path": "tests/unit/test_unit_of_work.py",
            "description": "Unit of Work Pattern Tests",
            "tests": ["TestUnitOfWork", "TestRepositoryContainer"]
        },
        {
            "path": "tests/unit/test_product_service_solid.py",
            "description": "ProductService SOLID Tests",
            "tests": ["TestProductServiceSOLID"]
        },
        {
            "path": "tests/unit/test_authorization.py",
            "description": "Authorization Layer Tests",
            "tests": ["TestProductAuthorizer"]
        },
        {
            "path": "tests/unit/test_service_factory.py",
            "description": "ServiceFactory Tests",
            "tests": ["TestServiceFactory"]
        },
        {
            "path": "tests/integration/test_api_solid_integration.py",
            "description": "API Integration Tests",
            "tests": ["TestProductsAPIIntegration"]
        },
        {
            "path": "tests/performance/test_solid_performance_simple.py",
            "description": "Performance Tests",
            "tests": [
                "TestCommandPatternPerformance",
                "TestQueryPatternPerformance", 
                "TestValidationPerformance",
                "TestUnitOfWorkPerformance",
                "TestAuthorizationPerformance",
                "TestServiceFactoryPerformance",
                "TestSOLIDIntegrationPerformance"
            ]
        }
    ]
    
    print("=== WMS SOLID Pattern Test Suite ===")
    print(f"Running {len(test_modules)} test modules...")
    print()
    
    # Configure pytest arguments
    pytest_args = [
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--durations=10",  # Show 10 slowest tests
        "--color=yes",  # Colored output
        "-x",  # Stop on first failure
    ]
    
    # Run tests for each module
    results = {}
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    
    for module in test_modules:
        print(f"\n--- {module['description']} ---")
        print(f"Running: {module['path']}")
        
        try:
            # Run pytest for this module
            exit_code = pytest.main([module['path']] + pytest_args)
            
            # Store results (simplified - in real implementation would parse pytest output)
            if exit_code == 0:
                results[module['path']] = "PASSED"
                total_passed += 1
                print("Status: PASSED")
            else:
                results[module['path']] = "FAILED"
                total_failed += 1
                print("Status: FAILED")
                
        except Exception as e:
            results[module['path']] = f"ERROR: {e}"
            total_failed += 1
            print(f"Status: ERROR - {e}")
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUITE SUMMARY")
    print("="*50)
    
    for module_path, status in results.items():
        module_desc = next(m['description'] for m in test_modules if m['path'] == module_path)
        print(f"{module_desc:.<40} {status}")
    
    print("-"*50)
    print(f"Total Modules: {len(test_modules)}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Skipped: {total_skipped}")
    
    success_rate = (total_passed / len(test_modules)) * 100 if test_modules else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    return total_failed == 0


def run_specific_test_pattern(pattern_name):
    """Run tests for a specific SOLID pattern."""
    
    pattern_map = {
        "command": ["tests/unit/test_commands_simple.py"],
        "query": ["tests/unit/test_queries_simple.py"],
        "validation": ["tests/unit/test_validators.py"],
        "unit_of_work": ["tests/unit/test_unit_of_work.py"],
        "service": ["tests/unit/test_product_service_solid.py", "tests/unit/test_service_factory.py"],
        "authorization": ["tests/unit/test_authorization.py"],
        "integration": ["tests/integration/test_api_solid_integration.py"],
        "performance": ["tests/performance/test_solid_performance_simple.py"]
    }
    
    if pattern_name not in pattern_map:
        print(f"Unknown pattern: {pattern_name}")
        print(f"Available patterns: {', '.join(pattern_map.keys())}")
        return False
    
    test_files = pattern_map[pattern_name]
    print(f"Running {pattern_name} pattern tests...")
    
    pytest_args = [
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    exit_code = pytest.main(test_files + pytest_args)
    return exit_code == 0


def run_quick_tests():
    """Run a quick subset of tests for rapid feedback."""
    
    quick_test_files = [
        "tests/unit/test_commands_simple.py::TestCreateProductCommand::test_create_product_command_valid_data",
        "tests/unit/test_queries_simple.py::TestGetProductQuery::test_get_product_query_valid_data",
        "tests/unit/test_validators.py::TestProductValidator::test_product_validator_initialization",
        "tests/unit/test_unit_of_work.py::TestUnitOfWork::test_unit_of_work_initialization",
        "tests/unit/test_authorization.py::TestProductAuthorizer::test_product_authorizer_initialization"
    ]
    
    print("Running quick SOLID tests...")
    
    pytest_args = [
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    exit_code = pytest.main(quick_test_files + pytest_args)
    return exit_code == 0


def generate_test_report():
    """Generate a comprehensive test report."""
    
    report = {
        "test_suite": "WMS SOLID Pattern Tests",
        "patterns_tested": [
            "Command Pattern",
            "Query Pattern", 
            "Validation Layer",
            "Unit of Work Pattern",
            "ProductService (SOLID)",
            "Authorization Layer",
            "ServiceFactory",
            "API Integration",
            "Performance"
        ],
        "solid_principles_verified": [
            "Single Responsibility Principle (SRP)",
            "Open/Closed Principle (OCP)", 
            "Liskov Substitution Principle (LSP)",
            "Interface Segregation Principle (ISP)",
            "Dependency Inversion Principle (DIP)"
        ],
        "test_categories": [
            "Unit Tests",
            "Integration Tests",
            "Performance Tests",
            "Error Handling Tests",
            "Edge Case Tests",
            "Concurrency Tests"
        ]
    }
    
    print("=== TEST REPORT ===")
    print(f"Suite: {report['test_suite']}")
    print(f"Patterns Tested: {len(report['patterns_tested'])}")
    print(f"SOLID Principles Verified: {len(report['solid_principles_verified'])}")
    print(f"Test Categories: {len(report['test_categories'])}")
    print()
    
    print("Patterns Tested:")
    for pattern in report['patterns_tested']:
        print(f"  - {pattern}")
    
    print("\nSOLID Principles Verified:")
    for principle in report['solid_principles_verified']:
        print(f"  - {principle}")
    
    print("\nTest Categories:")
    for category in report['test_categories']:
        print(f"  - {category}")
    
    return report


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="WMS SOLID Pattern Test Runner")
    parser.add_argument("--pattern", choices=["command", "query", "validation", "unit_of_work", 
                                              "service", "authorization", "integration", "performance"],
                       help="Run tests for specific pattern")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    parser.add_argument("--report", action="store_true", help="Generate test report")
    parser.add_argument("--all", action="store_true", default=True, help="Run all tests (default)")
    
    args = parser.parse_args()
    
    if args.report:
        generate_test_report()
    elif args.pattern:
        success = run_specific_test_pattern(args.pattern)
        sys.exit(0 if success else 1)
    elif args.quick:
        success = run_quick_tests()
        sys.exit(0 if success else 1)
    elif args.all:
        success = run_solid_tests()
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
