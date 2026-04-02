"""Comprehensive tests for advanced SQL injection validation."""

import pytest
import ast
from unittest.mock import Mock, patch
from app.core.advanced_validation import (
    SQLInjectionValidator,
    InputSanitizer,
    SecurityPolicyEnforcer,
    security_policy
)

class TestSQLInjectionValidator:
    """Test cases for SQL injection validator."""
    
    def test_word_boundary_validation_safe_inputs(self):
        """Test that safe inputs pass word-boundary validation."""
        safe_inputs = [
            "normal text",
            "user123",
            "product_name",
            "John Doe",
            "email@example.com",
            "2023-12-01",
            "123.45",
            "simple_query",
            "table_name",
            "column_value"
        ]
        
        for input_val in safe_inputs:
            is_valid, violations = SQLInjectionValidator.validate_with_word_boundaries(input_val, "test_field")
            assert is_valid, f"Safe input '{input_val}' should pass validation"
            assert len(violations) == 0, f"Safe input '{input_val}' should have no violations"
    
    def test_word_boundary_validation_sql_keywords(self):
        """Test that SQL keywords are detected with word boundaries."""
        dangerous_inputs = [
            ("SELECT", "SELECT keyword"),
            ("select * from users", "SELECT keyword in lowercase"),
            ("INSERT INTO", "INSERT keyword"),
            ("UPDATE table", "UPDATE keyword"),
            ("DELETE FROM", "DELETE keyword"),
            ("DROP TABLE", "DROP keyword"),
            ("CREATE VIEW", "CREATE keyword"),
            ("ALTER TABLE", "ALTER keyword"),
            ("TRUNCATE TABLE", "TRUNCATE keyword"),
            ("UNION SELECT", "UNION keyword"),
            ("EXEC sp_help", "EXEC keyword"),
            ("EXECUTE procedure", "EXECUTE keyword"),
            ("WAITFOR DELAY", "WAITFOR keyword"),
            ("BENCHMARK", "BENCHMARK keyword"),
            ("PG_SLEEP", "PG_SLEEP keyword")
        ]
        
        for input_val, description in dangerous_inputs:
            is_valid, violations = SQLInjectionValidator.validate_with_word_boundaries(input_val, "test_field")
            assert not is_valid, f"Dangerous input '{input_val}' ({description}) should fail validation"
            assert len(violations) > 0, f"Dangerous input '{input_val}' should have violations"
    
    def test_word_boundary_partial_word_safety(self):
        """Test that partial words containing SQL keywords are safe."""
        safe_partial_words = [
            "selection",  # Contains "select" but not as word boundary
            "updateable",  # Contains "update" but not as word boundary
            "deletion",   # Contains "delete" but not as word boundary
            "creation",   # Contains "create" but not as word boundary
            "executive",  # Contains "exec" but not as word boundary
            "selective",  # Contains "select" but not as word boundary
            "insertion",  # Contains "insert" but not as word boundary
            "droplet",    # Contains "drop" but not as word boundary
        ]
        
        for input_val in safe_partial_words:
            is_valid, violations = SQLInjectionValidator.validate_with_word_boundaries(input_val, "test_field")
            assert is_valid, f"Safe partial word '{input_val}' should pass validation"
            assert len(violations) == 0, f"Safe partial word '{input_val}' should have no violations"
    
    def test_comment_detection(self):
        """Test that SQL comments are detected."""
        comment_inputs = [
            "text -- comment",
            "text /* comment */",
            "text # comment",
            "SELECT * FROM users -- WHERE id = 1",
            "INSERT INTO table /* comment */ VALUES (1)",
        ]
        
        for input_val in comment_inputs:
            is_valid, violations = SQLInjectionValidator.validate_with_word_boundaries(input_val, "test_field")
            assert not is_valid, f"Comment input '{input_val}' should fail validation"
            assert any("comment" in v.lower() for v in violations), f"Should detect comment in '{input_val}'"
    
    def test_multiple_statement_detection(self):
        """Test that multiple SQL statements are detected."""
        multiple_statement_inputs = [
            "SELECT * FROM users; DROP TABLE users;",
            "INSERT INTO table VALUES (1); DELETE FROM table;",
            "UPDATE table SET col=1; SELECT * FROM table;",
        ]
        
        for input_val in multiple_statement_inputs:
            is_valid, violations = SQLInjectionValidator.validate_with_word_boundaries(input_val, "test_field")
            assert not is_valid, f"Multiple statement input '{input_val}' should fail validation"
            assert any("multiple" in v.lower() for v in violations), f"Should detect multiple statements in '{input_val}'"
    
    def test_ast_parsing_code_injection(self):
        """Test AST parsing for code injection detection."""
        dangerous_code_inputs = [
            "eval('malicious code')",
            "exec('system command')",
            "__import__('os')",
            "open('/etc/passwd')",
            "compile('code', 'exec')",
        ]
        
        for input_val in dangerous_code_inputs:
            is_valid, violations = SQLInjectionValidator.validate_with_ast_parsing(input_val, "test_field")
            assert not is_valid, f"Dangerous code '{input_val}' should fail AST validation"
            assert len(violations) > 0, f"Dangerous code '{input_val}' should have AST violations"
    
    def test_ast_parsing_safe_code(self):
        """Test that safe code passes AST validation."""
        safe_code_inputs = [
            "normal text",
            "user input data",
            "123 + 456",
            "simple string",
            "no code here",
        ]
        
        for input_val in safe_code_inputs:
            is_valid, violations = SQLInjectionValidator.validate_with_ast_parsing(input_val, "test_field")
            # Safe inputs might fail AST parsing if they're not valid Python, which is expected
            # The key is that no dangerous AST nodes should be detected
            dangerous_violations = [v for v in violations if "dangerous" in v.lower()]
            assert len(dangerous_violations) == 0, f"Safe code '{input_val}' should have no dangerous AST violations"
    
    def test_sql_structure_validation(self):
        """Test SQL structure validation."""
        safe_sql = "SELECT * FROM users WHERE id = :id"
        dangerous_sql = "SELECT * FROM users; DROP TABLE users;"
        
        # Test safe SQL
        is_valid, violations = SQLInjectionValidator.validate_sql_structure(safe_sql, {'SELECT'})
        assert is_valid, f"Safe SQL '{safe_sql}' should pass validation"
        assert len(violations) == 0, f"Safe SQL '{safe_sql}' should have no violations"
        
        # Test dangerous SQL
        is_valid, violations = SQLInjectionValidator.validate_sql_structure(dangerous_sql, {'SELECT'})
        assert not is_valid, f"Dangerous SQL '{dangerous_sql}' should fail validation"
        assert len(violations) > 0, f"Dangerous SQL '{dangerous_sql}' should have violations"
    
    def test_comprehensive_validation(self):
        """Test comprehensive validation combining all methods."""
        safe_input = "normal user input"
        dangerous_input = "SELECT * FROM users; DROP TABLE users;"
        
        # Test safe input
        is_valid, violations = SQLInjectionValidator.comprehensive_validate(safe_input, "test_field", "general")
        assert is_valid, f"Safe input '{safe_input}' should pass comprehensive validation"
        assert len(violations) == 0, f"Safe input '{safe_input}' should have no violations"
        
        # Test dangerous input
        is_valid, violations = SQLInjectionValidator.comprehensive_validate(dangerous_input, "test_field", "general")
        assert not is_valid, f"Dangerous input '{dangerous_input}' should fail comprehensive validation"
        assert len(violations) > 0, f"Dangerous input '{dangerous_input}' should have violations"

class TestInputSanitizer:
    """Test cases for input sanitization."""
    
    def test_sanitize_identifier(self):
        """Test identifier sanitization."""
        test_cases = [
            ("normal_identifier", "normal_identifier"),
            ("identifier123", "identifier123"),
            ("_identifier", "_identifier"),
            ("1identifier", "_1identifier"),  # Should prepend underscore
            ("identifier-with-dash", "identifierwithdash"),  # Should remove dash
            ("identifier with space", "identifierwithspace"),  # Should remove space
            ("identifier@symbol", "identifiersymbol"),  # Should remove @
            ("", ""),  # Empty string
            (None, ""),  # None input
            (123, ""),  # Non-string input
        ]
        
        for input_val, expected in test_cases:
            result = InputSanitizer.sanitize_identifier(input_val)
            assert result == expected, f"Sanitize identifier '{input_val}' should be '{expected}', got '{result}'"
    
    def test_sanitize_text_input(self):
        """Test text input sanitization."""
        test_cases = [
            ("normal text", "normal text"),
            ("text with -- comment", "text with"),  # Should remove comment
            ("text /* comment */ more", "text more"),  # Should remove comment
            ("text # comment", "text"),  # Should remove comment
            ("text\x00with\x00null", "textwithnull"),  # Should remove null bytes
            ("text    with    spaces", "text with spaces"),  # Should normalize whitespace
            ("", ""),  # Empty string
            (None, ""),  # None input
            (123, ""),  # Non-string input
        ]
        
        for input_val, expected in test_cases:
            result = InputSanitizer.sanitize_text_input(input_val)
            assert result == expected, f"Sanitize text '{input_val}' should be '{expected}', got '{result}'"
    
    def test_sanitize_numeric_input(self):
        """Test numeric input sanitization."""
        test_cases = [
            ("123", "123"),
            ("-456", "-456"),
            ("123.45", "123.45"),
            ("-78.90", "-78.90"),
            ("1e10", "1e10"),
            ("-2e-5", "-2e-5"),
            ("12a34", ""),  # Invalid numeric format
            ("abc", ""),  # Invalid numeric format
            ("", ""),  # Empty string
            (None, ""),  # None input
            (123, "123"),  # Number input
        ]
        
        for input_val, expected in test_cases:
            result = InputSanitizer.sanitize_numeric_input(str(input_val) if input_val is not None else input_val)
            assert result == expected, f"Sanitize numeric '{input_val}' should be '{expected}', got '{result}'"

class TestSecurityPolicyEnforcer:
    """Test cases for security policy enforcer."""
    
    def test_validate_table_name(self):
        """Test table name validation."""
        # Valid table names
        valid_names = ["users", "products", "warehouse_inventory", "table_123"]
        for name in valid_names:
            is_valid, violations = security_policy.validate_input(name, "table_name", "test_table")
            assert is_valid, f"Valid table name '{name}' should pass validation"
            assert len(violations) == 0, f"Valid table name '{name}' should have no violations"
        
        # Invalid table names
        invalid_names = ["SELECT", "users; DROP", "1table", "table-name", "table name", ""]
        for name in invalid_names:
            is_valid, violations = security_policy.validate_input(name, "table_name", "test_table")
            assert not is_valid, f"Invalid table name '{name}' should fail validation"
            assert len(violations) > 0, f"Invalid table name '{name}' should have violations"
    
    def test_validate_column_name(self):
        """Test column name validation."""
        # Valid column names
        valid_names = ["id", "name", "created_at", "user_id", "column_123"]
        for name in valid_names:
            is_valid, violations = security_policy.validate_input(name, "column_name", "test_column")
            assert is_valid, f"Valid column name '{name}' should pass validation"
            assert len(violations) == 0, f"Valid column name '{name}' should have no violations"
        
        # Invalid column names
        invalid_names = ["SELECT", "column; DROP", "1column", "column-name", "column name", ""]
        for name in invalid_names:
            is_valid, violations = security_policy.validate_input(name, "column_name", "test_column")
            assert not is_valid, f"Invalid column name '{name}' should fail validation"
            assert len(violations) > 0, f"Invalid column name '{name}' should have violations"
    
    def test_validate_sql_condition(self):
        """Test SQL condition validation."""
        # Valid conditions
        valid_conditions = [
            "id = :id",
            "name LIKE :name",
            "created_at > :date",
            "status IN (:statuses)",
            "price BETWEEN :min AND :max"
        ]
        for condition in valid_conditions:
            is_valid, violations = security_policy.validate_input(condition, "sql_condition", "test_condition")
            assert is_valid, f"Valid condition '{condition}' should pass validation"
            assert len(violations) == 0, f"Valid condition '{condition}' should have no violations"
        
        # Invalid conditions
        invalid_conditions = [
            "id = 1; DROP TABLE users",
            "SELECT * FROM users",
            "INSERT INTO table",
            "UPDATE table SET",
            "DELETE FROM table"
        ]
        for condition in invalid_conditions:
            is_valid, violations = security_policy.validate_input(condition, "sql_condition", "test_condition")
            assert not is_valid, f"Invalid condition '{condition}' should fail validation"
            assert len(violations) > 0, f"Invalid condition '{condition}' should have violations"
    
    def test_validate_user_input(self):
        """Test general user input validation."""
        # Valid inputs
        valid_inputs = ["John Doe", "email@example.com", "Product Name", "Normal text"]
        for input_val in valid_inputs:
            is_valid, violations = security_policy.validate_input(input_val, "user_input", "test_field")
            assert is_valid, f"Valid input '{input_val}' should pass validation"
            assert len(violations) == 0, f"Valid input '{input_val}' should have no violations"
        
        # Invalid inputs
        invalid_inputs = [
            "SELECT * FROM users",
            "'; DROP TABLE users; --",
            "eval('malicious')",
            "text with -- comment"
        ]
        for input_val in invalid_inputs:
            is_valid, violations = security_policy.validate_input(input_val, "user_input", "test_field")
            assert not is_valid, f"Invalid input '{input_val}' should fail validation"
            assert len(violations) > 0, f"Invalid input '{input_val}' should have violations"
    
    def test_validate_numeric_value(self):
        """Test numeric value validation."""
        # Valid numeric values
        valid_values = ["123", "-456", "123.45", "-78.90", "0"]
        for value in valid_values:
            is_valid, violations = security_policy.validate_input(value, "numeric_value", "test_numeric")
            assert is_valid, f"Valid numeric '{value}' should pass validation"
            assert len(violations) == 0, f"Valid numeric '{value}' should have no violations"
        
        # Invalid numeric values
        invalid_values = ["12a34", "abc", "SELECT", "123; DROP", ""]
        for value in invalid_values:
            is_valid, violations = security_policy.validate_input(value, "numeric_value", "test_numeric")
            assert not is_valid, f"Invalid numeric '{value}' should fail validation"
            assert len(violations) > 0, f"Invalid numeric '{value}' should have violations"
    
    def test_sanitize_input(self):
        """Test input sanitization."""
        test_cases = [
            ("identifier", "identifier", "identifier"),
            ("1identifier", "_1identifier", "identifier"),
            ("table-name", "tablename", "identifier"),
            ("normal text", "normal text", "text"),
            ("text -- comment", "text", "text"),
            ("123", "123", "numeric"),
            ("12a34", "", "numeric"),
        ]
        
        for input_val, expected, context in test_cases:
            result = security_policy.sanitize_input(input_val, context)
            assert result == expected, f"Sanitize '{input_val}' as {context} should be '{expected}', got '{result}'"

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_and_null_inputs(self):
        """Test empty and null inputs."""
        test_cases = [
            ("", "empty string"),
            (None, "None input"),
            (0, "zero integer"),
            (0.0, "zero float"),
            (False, "False boolean"),
            ([], "empty list"),
            ({}, "empty dict"),
        ]
        
        for input_val, description in test_cases:
            # Test with word-boundary validation
            is_valid, violations = SQLInjectionValidator.validate_with_word_boundaries(input_val, "test_field")
            # Empty/null inputs should either pass or fail gracefully without errors
            assert isinstance(is_valid, bool), f"{description} should return boolean"
            assert isinstance(violations, list), f"{description} should return list of violations"
    
    def test_very_long_inputs(self):
        """Test very long inputs."""
        very_long_input = "a" * 10000  # 10KB string
        
        is_valid, violations = SQLInjectionValidator.validate_with_word_boundaries(very_long_input, "test_field")
        assert not is_valid, "Very long input should fail validation"
        assert any("too long" in v.lower() for v in violations), "Should detect input too long"
    
    def test_unicode_inputs(self):
        """Test Unicode inputs."""
        unicode_inputs = [
            "café résumé naïve",
            "用户输入",  # Chinese characters
            "пользователь",  # Cyrillic characters
            "مستخدم",  # Arabic characters
            "🚀 emoji test",
        ]
        
        for input_val in unicode_inputs:
            is_valid, violations = SQLInjectionValidator.validate_with_word_boundaries(input_val, "test_field")
            # Unicode inputs should be handled safely
            assert isinstance(is_valid, bool), f"Unicode input '{input_val}' should return boolean"
            assert isinstance(violations, list), f"Unicode input '{input_val}' should return list"
    
    def test_special_characters(self):
        """Test special characters."""
        special_chars = [
            "!@#$%^&*()",
            "[]{}|\\",
            "\"'`",
            "<>",
            "\t\n\r",
            "\x00\x01\x02",  # Control characters
        ]
        
        for input_val in special_chars:
            is_valid, violations = SQLInjectionValidator.validate_with_word_boundaries(input_val, "test_field")
            # Special characters should be handled safely
            assert isinstance(is_valid, bool), f"Special chars '{input_val}' should return boolean"
            assert isinstance(violations, list), f"Special chars '{input_val}' should return list"

class TestPerformance:
    """Performance tests for validation."""
    
    def test_validation_performance(self):
        """Test that validation doesn't have performance issues."""
        import time
        
        # Test with large number of inputs
        test_inputs = ["normal input"] * 1000
        
        start_time = time.time()
        for input_val in test_inputs:
            SQLInjectionValidator.validate_with_word_boundaries(input_val, "test_field")
        end_time = time.time()
        
        # Should complete 1000 validations in reasonable time (< 1 second)
        assert end_time - start_time < 1.0, "1000 validations should complete in < 1 second"
    
    def test_large_input_performance(self):
        """Test performance with large inputs."""
        import time
        
        large_input = "a" * 1000  # 1KB string
        
        start_time = time.time()
        SQLInjectionValidator.validate_with_word_boundaries(large_input, "test_field")
        end_time = time.time()
        
        # Should complete large input validation quickly (< 0.1 seconds)
        assert end_time - start_time < 0.1, "Large input validation should complete in < 0.1 seconds"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
