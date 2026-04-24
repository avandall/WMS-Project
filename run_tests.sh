#!/bin/bash

# Test runner script for WMS project
# This script ensures PYTHONPATH is set correctly before running pytest

set -e

# Set PYTHONPATH to include src directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Run pytest with all arguments passed to this script
echo "Running tests with PYTHONPATH=${PYTHONPATH}"
pytest "$@"
