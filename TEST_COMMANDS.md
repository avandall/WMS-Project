# WMS Test Commands Quick Reference

## 🚀 **Easy Test Running**

### **Using the Test Runner (Recommended)**
```bash
# Fast tests (unit + smoke) - great for development
python run_tests.py --fast

# All tests with verbose output
python run_tests.py --all --verbose

# Specific test categories
python run_tests.py --unit          # Unit tests only
python run_tests.py --sql           # SQL tests only
python run_tests.py --security      # Security tests only
python run_tests.py --ai            # AI tests only

# With coverage report
python run_tests.py --unit --coverage

# Parallel execution (faster)
python run_tests.py --unit --parallel
```

### **Using Safe Pytest (NEW!)**
```bash
# Safe pytest wrapper that bypasses I/O issues
./pytest-safe

# This runs: tests/unit/ tests/sql/ tests/test_smoke.py
# Result: 314 tests pass 
```

## 📋 **Direct Pytest Commands**

### **Working Commands**
```bash
# Unit tests (225 tests pass)
python -m pytest tests/unit/ -v

# SQL tests (83 tests pass)
python -m pytest tests/sql/ -v

# Smoke tests (6 tests pass)
python -m pytest tests/test_smoke.py -v

# Combined working tests
python -m pytest tests/unit/ tests/sql/ tests/test_smoke.py -v
```

### **⚠️ Problematic Commands**
```bash
# ❌ These fail with I/O error
pytest
python -m pytest
python -m pytest tests/
python -m pytest tests/ -v

# Error: ValueError: I/O operation on closed file
```

## 🎯 **Test Categories Summary**

| Category | Command | Count | Status |
|----------|---------|-------|--------|
| Unit Tests | `python -m pytest tests/unit/ -v` | 225 | Working |
| SQL Tests | `python -m pytest tests/sql/ -v` | 83 | Working |
| Smoke Tests | `python -m pytest tests/test_smoke.py -v` | 6 | Working |
| Security Tests | `python scripts/run_sql_exec_tests.py` | 15 | Working |
| AI Tests | `python tests/test_relevance_filter.py` | 46 | Working |

## 🔧 **Development Workflow**

### **During Development**
```bash
# Quick check
./pytest-safe

# Or using test runner
python run_tests.py --fast

# After code changes
python run_tests.py --unit --verbose

# After database changes
python run_tests.py --sql --verbose
```

### **Before Commit**
```bash
# Full check
python run_tests.py --all --verbose

# Or use safe pytest
./pytest-safe
```

### **For CI/CD**
```bash
# What GitHub Actions runs
python run_tests.py --unit --sql --security --ai
```

## 📊 **Performance Tips**

### **Fast Execution**
```bash
# Parallel testing
python run_tests.py --unit --parallel

# Skip slow tests
python run_tests.py --fast

# Only run failed tests
python -m pytest tests/unit/ --lf
```

### **Coverage**
```bash
# Coverage report
python run_tests.py --unit --coverage

# HTML coverage (opens in browser)
python -m pytest tests/unit/ --cov=src --cov-report=html
```

## 🐛 **Troubleshooting**

### **Common Issues**
```bash
# Module not found - ensure venv activated
source .venv/bin/activate

# Import errors - check Python path
python -c "import sys; print(sys.path)"

# Database errors - SQL tests use in-memory SQLite
# No external database needed
```

### **Debug Mode**
```bash
# Run with debugger
python -m pytest tests/unit/ -v --pdb

# Show local variables
python -m pytest tests/unit/ -v --tb=long

# Print output
python -m pytest tests/unit/ -v -s
```

## 🎯 **Best Practices**

1. **Use safe pytest**: `./pytest-safe` avoids all I/O issues
2. **Use test runner**: `python run_tests.py` provides best interface
3. **Run specific categories**: `--unit`, `--sql`, `--smoke`
4. **Always use verbose**: `--verbose` for better output
5. **Check before commit**: `python run_tests.py --fast`

## 📝 **Commands Summary**

```bash
# BEST OPTIONS (choose one):
./pytest-safe                    # Safe pytest (314 tests)
python run_tests.py --fast        # Quick check
python run_tests.py --unit        # Unit tests only
python run_tests.py --sql         # SQL tests only
python run_tests.py --all         # All tests

# AVOID THESE:
pytest                           # I/O error
python -m pytest                  # I/O error
```
2. **Run specific categories** - `--unit`, `--sql`, `--security`
3. **Use `--fast` for development** - unit + smoke tests
4. **Use `--verbose` for detailed output**
5. **Always run tests before committing**

---

**Remember**: The test runner solves all pytest I/O issues and provides a convenient interface for running tests!
