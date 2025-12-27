#!/usr/bin/env python3
"""
Test runner script for PMKT Warehouse Management System.
"""
import subprocess
import sys
import argparse
from pathlib import Path


def run_tests(test_type=None, coverage=True, verbose=False):
    """Run the test suite."""
    cmd = [sys.executable, "-m", "pytest"]

    if test_type:
        if test_type == "unit":
            cmd.append("tests/unit/")
        elif test_type == "integration":
            cmd.append("tests/integration/")
        elif test_type == "functional":
            cmd.append("tests/functional/")
        else:
            print(f"Unknown test type: {test_type}")
            return 1

    if coverage:
        cmd.extend(["--cov=PMKT", "--cov-report=term-missing"])

    if verbose:
        cmd.append("-v")

    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run PMKT tests")
    parser.add_argument(
        "test_type",
        nargs="?",
        choices=["unit", "integration", "functional"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Skip coverage reporting"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    return run_tests(
        test_type=args.test_type,
        coverage=not args.no_coverage,
        verbose=args.verbose
    )


if __name__ == "__main__":
    sys.exit(main())