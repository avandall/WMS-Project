"""Comprehensive unit tests for enhanced AI chains."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

from app.infrastructure.ai.enhanced_chains import (
    SQLExtractor,
    EnhancedAIChains,
    SQLGenerationMetrics,
    enhanced_chains
)

class TestSQLExtractor:
    """Test cases for SQLExtractor."""
    
    def test_extract_sql_standard_markdown(self):
        """Test SQL extraction from standard markdown blocks."""
        test_cases = [
            # Standard SQL block
            ("```sql\nSELECT * FROM users\n```", "SELECT * FROM users"),
            # SQL block with uppercase
            ("```SQL\nSELECT * FROM products\n```", "SELECT * FROM products"),
            # PostgreSQL block
            ("```postgresql\nSELECT id, name FROM items\n```", "SELECT id, name FROM items"),
            # Generic code block
            ("```\nSELECT count(*) FROM orders\n```", "SELECT count(*) FROM orders"),
            # With extra whitespace
            ("```sql\n\n  SELECT * FROM users  \n\n```", "SELECT * FROM users"),
        ]
        
        for input_text, expected in test_cases:
            result, issues = SQLExtractor.extract_sql(input_text)
            assert result == expected, f"Failed to extract from: {input_text}"
            assert len(issues) == 0, f"Unexpected issues for: {input_text}"
    
    def test_extract_sql_with_markers(self):
        """Test SQL extraction with text markers."""
        test_cases = [
            # SQL marker
            ("SQL:\nSELECT * FROM users", "SELECT * FROM users"),
            # Query marker
            ("Query:\nSELECT name FROM products", "SELECT name FROM products"),
            # Inline SQL with backticks
            ("Here's the query: `SELECT * FROM users` for you", "SELECT * FROM users"),
            # Inline SQL with quotes
            ('The query is "SELECT id FROM items"', "SELECT id FROM items"),
        ]
        
        for input_text, expected in test_cases:
            result, issues = SQLExtractor.extract_sql(input_text)
            assert result == expected, f"Failed to extract from: {input_text}"
            assert len(issues) == 0, f"Unexpected issues for: {input_text}"
    
    def test_extract_sql_no_patterns(self):
        """Test SQL extraction when no patterns match."""
        test_cases = [
            "SELECT * FROM users",
            "  SELECT name, email FROM customers  ",
            "WITH cte AS (SELECT * FROM products) SELECT * FROM cte",
        ]
        
        for input_text in test_cases:
            result, issues = SQLExtractor.extract_sql(input_text)
            assert result == input_text.strip(), f"Should return original text for: {input_text}"
            assert len(issues) == 0, f"Unexpected issues for: {input_text}"
    
    def test_extract_sql_cleanup(self):
        """Test SQL cleanup functionality."""
        test_cases = [
            # Remove comments
            ("SELECT * FROM users -- comment", "SELECT * FROM users"),
            # Remove block comments
            ("SELECT * /* comment */ FROM users", "SELECT * FROM users"),
            # Normalize whitespace
            ("SELECT   *   FROM   users", "SELECT * FROM users"),
            # Remove trailing semicolon
            ("SELECT * FROM users;", "SELECT * FROM users"),
            # Combined cleanup
            ("SELECT * /* comment */ FROM users -- another\n;", "SELECT * FROM users"),
        ]
        
        for input_text, expected in test_cases:
            result, issues = SQLExtractor.extract_sql(input_text)
            assert result == expected, f"Cleanup failed for: {input_text}"
            assert len(issues) == 0, f"Unexpected issues for: {input_text}"
    
    def test_extract_sql_validation_issues(self):
        """Test SQL validation issues detection."""
        test_cases = [
            # Empty SQL
            ("", ["Extracted SQL is empty"]),
            # Too short
            ("SEL", ["SQL too short to be valid"]),
            # No SELECT/WITH
            ("INSERT INTO users", ["SQL does not contain SELECT or WITH"]),
            # Dangerous operations
            ("SELECT * FROM users; DROP TABLE users", ["Suspicious pattern detected: drop\\s+table"]),
            # Multiple issues
            ("", ["Extracted SQL is empty", "SQL too short to be valid"]),
        ]
        
        for input_text, expected_issues in test_cases:
            result, issues = SQLExtractor.extract_sql(input_text)
            if expected_issues:
                assert len(issues) > 0, f"Expected issues for: {input_text}"
                for expected_issue in expected_issues:
                    assert any(expected_issue in issue for issue in issues), f"Missing expected issue: {expected_issue}"
    
    def test_extract_sql_edge_cases(self):
        """Test edge cases for SQL extraction."""
        test_cases = [
            # Multiple blocks - should take first
            ("```sql\nSELECT * FROM users\n```\nSome text\n```sql\nSELECT * FROM products\n```", "SELECT * FROM users"),
            # Nested backticks
            ("```sql\nSELECT `name` FROM users\n```", "SELECT `name` FROM users"),
            # Mixed case SQL keywords
            ("```sql\nSelect * From Users\n```", "Select * From Users"),
            # Unicode characters
            ("```sql\nSELECT * FROM 用户\n```", "SELECT * FROM 用户"),
            # Very long SQL
            ("```sql\n" + "SELECT * FROM users WHERE " + " ".join([f"col{i}=i" for i in range(100)]) + "\n```", 
             "SELECT * FROM users WHERE " + " ".join([f"col{i}=i" for i in range(100)])),
        ]
        
        for input_text in test_cases:
            result, issues = SQLExtractor.extract_sql(input_text)
            assert result, f"Should extract SQL from: {input_text}"
            # Should not have validation issues for valid SQL
            if "SELECT" in result.upper() and len(result) > 10:
                assert len(issues) == 0, f"Unexpected validation issues for valid SQL: {result}"
    
    def test_extract_sql_error_handling(self):
        """Test error handling in SQL extraction."""
        # Test with None input
        result, issues = SQLExtractor.extract_sql(None)
        assert result == ""
        assert len(issues) > 0
        assert any("Empty input" in issue for issue in issues)
        
        # Test with non-string input
        result, issues = SQLExtractor.extract_sql(123)
        assert result == ""
        assert len(issues) > 0

class TestEnhancedAIChains:
    """Test cases for EnhancedAIChains."""
    
    @patch('app.infrastructure.ai.enhanced_chains.get_langchain_db')
    @patch('app.infrastructure.ai.enhanced_chains.get_chat_model')
    def test_generate_sql_from_question_success(self, mock_get_model, mock_get_db):
        """Test successful SQL generation."""
        # Mock dependencies
        mock_db = Mock()
        mock_db.get_table_info.return_value = "users(id, name, email)"
        mock_get_db.return_value = mock_db
        
        mock_llm = Mock()
        mock_chain = Mock()
        mock_chain.invoke.return_value = "```sql\nSELECT * FROM users\n```"
        mock_llm.return_value = mock_chain
        mock_get_model.return_value = mock_llm
        
        # Test
        chains = EnhancedAIChains()
        sql, metrics = chains.generate_sql_from_question("Show me all users")
        
        # Assertions
        assert sql == "SELECT * FROM users"
        assert metrics.success is True
        assert metrics.question_length == len("Show me all users")
        assert metrics.sql_length == len("SELECT * FROM users")
        assert metrics.generation_time_ms > 0
        assert len(metrics.validation_violations) == 0
    
    @patch('app.infrastructure.ai.enhanced_chains.get_langchain_db')
    @patch('app.infrastructure.ai.enhanced_chains.get_chat_model')
    def test_generate_sql_from_question_validation_failure(self, mock_get_model, mock_get_db):
        """Test SQL generation with validation failure."""
        # Mock dependencies
        mock_db = Mock()
        mock_db.get_table_info.return_value = "users(id, name, email)"
        mock_get_db.return_value = mock_db
        
        mock_llm = Mock()
        mock_chain = Mock()
        mock_chain.invoke.return_value = "```sql\nDROP TABLE users\n```"  # Dangerous SQL
        mock_llm.return_value = mock_chain
        mock_get_model.return_value = mock_llm
        
        # Test
        chains = EnhancedAIChains()
        sql, metrics = chains.generate_sql_from_question("Delete all users")
        
        # Assertions
        assert sql == "DROP TABLE users"  # Still extracted but flagged
        assert metrics.success is False
        assert metrics.error_type == "Validation"
        assert len(metrics.validation_violations) > 0
        assert any("Suspicious pattern" in violation for violation in metrics.validation_violations)
    
    @patch('app.infrastructure.ai.enhanced_chains.get_chat_model')
    def test_generate_sql_from_question_llm_error(self, mock_get_model):
        """Test SQL generation with LLM error."""
        # Mock LLM error
        mock_llm = Mock()
        mock_chain = Mock()
        mock_chain.invoke.side_effect = Exception("LLM API error")
        mock_llm.return_value = mock_chain
        mock_get_model.return_value = mock_llm
        
        # Test
        chains = EnhancedAIChains()
        sql, metrics = chains.generate_sql_from_question("Test question")
        
        # Assertions
        assert sql == ""
        assert metrics.success is False
        assert metrics.error_type == "Exception"
        assert "LLM API error" in metrics.error_message
        assert metrics.generation_time_ms > 0
    
    @patch('app.infrastructure.ai.enhanced_chains.engine')
    def test_execute_sql_with_logging_success(self, mock_engine):
        """Test successful SQL execution with logging."""
        # Mock database execution
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.mappings.return_value.fetchmany.return_value = [
            {"id": 1, "name": "John"},
            {"id": 2, "name": "Jane"}
        ]
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        # Test
        chains = EnhancedAIChains()
        rows, execution_time = chains.execute_sql_with_logging("SELECT * FROM users")
        
        # Assertions
        assert len(rows) == 2
        assert rows[0]["id"] == 1
        assert rows[0]["name"] == "John"
        assert execution_time > 0
    
    @patch('app.infrastructure.ai.enhanced_chains.engine')
    def test_execute_sql_with_logging_validation_error(self, mock_engine):
        """Test SQL execution with validation error."""
        # Test with dangerous SQL
        chains = EnhancedAIChains()
        
        with pytest.raises(ValueError, match="SQL validation failed"):
            chains.execute_sql_with_logging("DROP TABLE users")
    
    @patch('app.infrastructure.ai.enhanced_chains.engine')
    def test_execute_sql_with_logging_database_error(self, mock_engine):
        """Test SQL execution with database error."""
        # Mock database error
        mock_conn = Mock()
        mock_conn.execute.side_effect = Exception("Database connection failed")
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        # Test
        chains = EnhancedAIChains()
        
        with pytest.raises(Exception, match="Database connection failed"):
            chains.execute_sql_with_logging("SELECT * FROM users")
    
    @patch('app.infrastructure.ai.enhanced_chains.get_chat_model')
    def test_summarize_rows_with_logging_success(self, mock_get_model):
        """Test successful row summarization."""
        # Mock LLM
        mock_llm = Mock()
        mock_chain = Mock()
        mock_chain.invoke.return_value = "Found 2 users: John and Jane"
        mock_llm.return_value = mock_chain
        mock_get_model.return_value = mock_llm
        
        # Test
        chains = EnhancedAIChains()
        rows = [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]
        answer = chains.summarize_rows_with_logging("Show users", "SELECT * FROM users", rows)
        
        # Assertions
        assert answer == "Found 2 users: John and Jane"
    
    @patch('app.infrastructure.ai.enhanced_chains.get_chat_model')
    def test_summarize_rows_with_logging_error(self, mock_get_model):
        """Test row summarization with error."""
        # Mock LLM error
        mock_llm = Mock()
        mock_chain = Mock()
        mock_chain.invoke.side_effect = Exception("LLM error")
        mock_llm.return_value = mock_chain
        mock_get_model.return_value = mock_llm
        
        # Test
        chains = EnhancedAIChains()
        answer = chains.summarize_rows_with_logging("Test", "SELECT * FROM users", [])
        
        # Should return safe fallback message
        assert "I apologize" in answer
    
    @patch('app.infrastructure.ai.enhanced_chains.get_chat_model')
    def test_is_relevant_query_with_logging_success(self, mock_get_model):
        """Test successful relevance check."""
        # Mock LLM
        mock_llm = Mock()
        mock_chain = Mock()
        mock_chain.invoke.return_value = "True"
        mock_llm.return_value = mock_chain
        mock_get_model.return_value = mock_llm
        
        # Test
        chains = EnhancedAIChains()
        is_relevant = chains.is_relevant_query_with_logging("Show me products")
        
        # Assertions
        assert is_relevant is True
    
    @patch('app.infrastructure.ai.enhanced_chains.get_chat_model')
    def test_is_relevant_query_with_logging_false(self, mock_get_model):
        """Test relevance check returning false."""
        # Mock LLM
        mock_llm = Mock()
        mock_chain = Mock()
        mock_chain.invoke.return_value = "False"
        mock_llm.return_value = mock_chain
        mock_get_model.return_value = mock_llm
        
        # Test
        chains = EnhancedAIChains()
        is_relevant = chains.is_relevant_query_with_logging("What's the weather?")
        
        # Assertions
        assert is_relevant is False
    
    @patch('app.infrastructure.ai.enhanced_chains.get_chat_model')
    def test_is_relevant_query_with_logging_error(self, mock_get_model):
        """Test relevance check with error."""
        # Mock LLM error
        mock_llm = Mock()
        mock_chain = Mock()
        mock_chain.invoke.side_effect = Exception("LLM error")
        mock_llm.return_value = mock_chain
        mock_get_model.return_value = mock_llm
        
        # Test
        chains = EnhancedAIChains()
        is_relevant = chains.is_relevant_query_with_logging("Test question")
        
        # Should default to False on error
        assert is_relevant is False
    
    @patch.object(EnhancedAIChains, 'is_relevant_query_with_logging')
    def test_handle_customer_chat_greeting(self, mock_relevance):
        """Test customer chat with greeting."""
        mock_relevance.return_value = False  # Should not be called for greetings
        
        # Test
        chains = EnhancedAIChains()
        response = chains.handle_customer_chat_with_db("hello")
        
        # Assertions
        assert response["sql"] == ""
        assert response["rows"] == []
        assert "Hi!" in response["answer"]
        assert response["metrics"].success is True
    
    @patch.object(EnhancedAIChains, 'is_relevant_query_with_logging')
    def test_handle_customer_chat_irrelevant(self, mock_relevance):
        """Test customer chat with irrelevant query."""
        mock_relevance.return_value = False
        
        # Test
        chains = EnhancedAIChains()
        response = chains.handle_customer_chat_with_db("What's the weather?")
        
        # Assertions
        assert response["sql"] == ""
        assert response["rows"] == []
        assert "Xin lỗi" in response["answer"]
        assert response["metrics"].success is False
        assert response["metrics"].error_type == "Relevance"
    
    @patch.object(EnhancedAIChains, 'is_relevant_query_with_logging')
    @patch.object(EnhancedAIChains, 'generate_sql_from_question')
    @patch.object(EnhancedAIChains, 'execute_sql_with_logging')
    @patch.object(EnhancedAIChains, 'summarize_rows_with_logging')
    def test_handle_customer_chat_direct_sql(self, mock_summarize, mock_execute, mock_generate, mock_relevance):
        """Test customer chat with direct SQL."""
        mock_relevance.return_value = True
        mock_execute.return_value = ([{"id": 1, "name": "Test"}], 10.0)
        mock_summarize.return_value = "Found 1 item"
        
        # Test
        chains = EnhancedAIChains()
        response = chains.handle_customer_chat_with_db("sql: SELECT * FROM users")
        
        # Assertions
        assert response["sql"] == "SELECT * FROM users"
        assert len(response["rows"]) == 1
        assert response["answer"] == "Found 1 item"
        mock_execute.assert_called_once()
        mock_summarize.assert_called_once()
        # generate should not be called for direct SQL
        mock_generate.assert_not_called()
    
    @patch.object(EnhancedAIChains, 'is_relevant_query_with_logging')
    @patch.object(EnhancedAIChains, 'generate_sql_from_question')
    @patch.object(EnhancedAIChains, 'execute_sql_with_logging')
    @patch.object(EnhancedAIChains, 'summarize_rows_with_logging')
    def test_handle_customer_chat_full_flow(self, mock_summarize, mock_execute, mock_generate, mock_relevance):
        """Test full customer chat flow."""
        mock_relevance.return_value = True
        mock_generate.return_value = ("SELECT * FROM users", Mock(success=True))
        mock_execute.return_value = ([{"id": 1, "name": "Test"}], 15.0)
        mock_summarize.return_value = "Found 1 user"
        
        # Test
        chains = EnhancedAIChains()
        response = chains.handle_customer_chat_with_db("Show me users")
        
        # Assertions
        assert response["sql"] == "SELECT * FROM users"
        assert len(response["rows"]) == 1
        assert response["answer"] == "Found 1 user"
        mock_relevance.assert_called_once()
        mock_generate.assert_called_once()
        mock_execute.assert_called_once()
        mock_summarize.assert_called_once()
    
    def test_get_performance_metrics_empty(self):
        """Test performance metrics with no history."""
        chains = EnhancedAIChains()
        metrics = chains.get_performance_metrics()
        
        assert metrics["message"] == "No metrics available"
    
    def test_get_performance_metrics_with_data(self):
        """Test performance metrics with data."""
        chains = EnhancedAIChains()
        
        # Add some metrics
        chains.metrics_history = [
            SQLGenerationMetrics(
                question_length=10, sql_length=20, generation_time_ms=100,
                execution_time_ms=50, row_count=5, validation_violations=[],
                success=True
            ),
            SQLGenerationMetrics(
                question_length=15, sql_length=25, generation_time_ms=120,
                execution_time_ms=60, row_count=0, validation_violations=["Error"],
                success=False, error_type="Validation"
            ),
        ]
        
        metrics = chains.get_performance_metrics()
        
        assert metrics["total_requests"] == 2
        assert metrics["successful_requests"] == 1
        assert metrics["failed_requests"] == 1
        assert metrics["success_rate"] == 50.0
        assert metrics["avg_generation_time_ms"] == 110.0
        assert metrics["avg_sql_length"] == 22.5
        assert metrics["avg_row_count"] == 2.5
        assert "Validation" in metrics["common_errors"]

class TestBackwardCompatibility:
    """Test backward compatibility functions."""
    
    @patch('app.infrastructure.ai.enhanced_chains.enhanced_chains')
    def test_generate_sql_from_question_compatibility(self, mock_enhanced):
        """Test backward compatibility for generate_sql_from_question."""
        mock_enhanced.generate_sql_from_question.return_value = ("SELECT * FROM users", Mock())
        
        # Import and test the compatibility function
        from app.infrastructure.ai.enhanced_chains import generate_sql_from_question
        
        result = generate_sql_from_question("Test question")
        assert result == "SELECT * FROM users"
        mock_enhanced.generate_sql_from_question.assert_called_once_with("Test question")
    
    @patch('app.infrastructure.ai.enhanced_chains.enhanced_chains')
    def test_summarize_rows_compatibility(self, mock_enhanced):
        """Test backward compatibility for summarize_rows."""
        mock_enhanced.summarize_rows_with_logging.return_value = "Summary text"
        
        from app.infrastructure.ai.enhanced_chains import summarize_rows
        
        result = summarize_rows("Question", "SQL", [])
        assert result == "Summary text"
        mock_enhanced.summarize_rows_with_logging.assert_called_once_with("Question", "SQL", [])
    
    @patch('app.infrastructure.ai.enhanced_chains.enhanced_chains')
    def test_is_relevant_query_compatibility(self, mock_enhanced):
        """Test backward compatibility for is_relevant_query."""
        mock_enhanced.is_relevant_query_with_logging.return_value = True
        
        from app.infrastructure.ai.enhanced_chains import is_relevant_query
        
        result = is_relevant_query("Test question")
        assert result is True
        mock_enhanced.is_relevant_query_with_logging.assert_called_once_with("Test question")
    
    @patch('app.infrastructure.ai.enhanced_chains.enhanced_chains')
    def test_handle_customer_chat_with_db_compatibility(self, mock_enhanced):
        """Test backward compatibility for handle_customer_chat_with_db."""
        mock_response = {"sql": "", "rows": [], "answer": "Test answer"}
        mock_enhanced.handle_customer_chat_with_db.return_value = mock_response
        
        from app.infrastructure.ai.enhanced_chains import handle_customer_chat_with_db
        
        result = handle_customer_chat_with_db("Test message")
        assert result == mock_response
        mock_enhanced.handle_customer_chat_with_db.assert_called_once_with("Test message")
    
    def test_extract_sql_compatibility(self):
        """Test backward compatibility for _extract_sql."""
        from app.infrastructure.ai.enhanced_chains import _extract_sql
        
        result = _extract_sql("```sql\nSELECT * FROM users\n```")
        assert result == "SELECT * FROM users"

class TestSQLGenerationMetrics:
    """Test SQLGenerationMetrics dataclass."""
    
    def test_metrics_creation(self):
        """Test metrics creation with all fields."""
        metrics = SQLGenerationMetrics(
            question_length=100,
            sql_length=50,
            generation_time_ms=200.5,
            execution_time_ms=150.3,
            row_count=10,
            validation_violations=[],
            success=True
        )
        
        assert metrics.question_length == 100
        assert metrics.sql_length == 50
        assert metrics.generation_time_ms == 200.5
        assert metrics.execution_time_ms == 150.3
        assert metrics.row_count == 10
        assert metrics.validation_violations == []
        assert metrics.success is True
        assert metrics.error_type is None
        assert metrics.error_message is None
    
    def test_metrics_with_errors(self):
        """Test metrics creation with error information."""
        metrics = SQLGenerationMetrics(
            question_length=50,
            sql_length=0,
            generation_time_ms=100.0,
            execution_time_ms=0,
            row_count=0,
            validation_violations=["Validation error"],
            success=False,
            error_type="ValidationError",
            error_message="SQL validation failed"
        )
        
        assert metrics.success is False
        assert metrics.error_type == "ValidationError"
        assert metrics.error_message == "SQL validation failed"
        assert len(metrics.validation_violations) == 1

class TestIntegration:
    """Integration tests for the enhanced chains system."""
    
    def test_sql_extractor_integration(self):
        """Test SQL extractor with various real-world inputs."""
        test_cases = [
            # Real LLM output examples
            ("Based on your question, here's the SQL query:\n\n```sql\nSELECT id, name FROM products WHERE price > 100\n```", 
             "SELECT id, name FROM products WHERE price > 100"),
            
            ("Here's your query:\n\n```\nWITH ranked_products AS (\n  SELECT *, ROW_NUMBER() OVER (ORDER BY price DESC) as rn\n  FROM products\n)\nSELECT * FROM ranked_products WHERE rn <= 10\n```\n\nThis will show you the top 10 products by price.",
             "WITH ranked_products AS (\n  SELECT *, ROW_NUMBER() OVER (ORDER BY price DESC) as rn\n  FROM products\n)\nSELECT * FROM ranked_products WHERE rn <= 10"),
            
            ("The query you need is: `SELECT COUNT(*) as total_users FROM users WHERE created_at > '2023-01-01'`",
             "SELECT COUNT(*) as total_users FROM users WHERE created_at > '2023-01-01'"),
        ]
        
        for input_text, expected in test_cases:
            result, issues = SQLExtractor.extract_sql(input_text)
            assert result == expected, f"Integration test failed for: {input_text}"
            assert len(issues) == 0, f"Unexpected issues for: {input_text}"
    
    def test_end_to_end_flow_simulation(self):
        """Test simulated end-to-end flow without external dependencies."""
        chains = EnhancedAIChains()
        
        # Test metrics tracking
        initial_metrics_count = len(chains.metrics_history)
        
        # Simulate adding metrics
        metrics1 = SQLGenerationMetrics(
            question_length=20, sql_length=30, generation_time_ms=150,
            execution_time_ms=100, row_count=5, validation_violations=[],
            success=True
        )
        chains.metrics_history.append(metrics1)
        
        metrics2 = SQLGenerationMetrics(
            question_length=25, sql_length=0, generation_time_ms=200,
            execution_time_ms=0, row_count=0, validation_violations=["Error"],
            success=False, error_type="Validation"
        )
        chains.metrics_history.append(metrics2)
        
        # Test performance metrics
        perf_metrics = chains.get_performance_metrics()
        assert perf_metrics["total_requests"] == 2
        assert perf_metrics["successful_requests"] == 1
        assert perf_metrics["failed_requests"] == 1
        assert perf_metrics["success_rate"] == 50.0
        
        # Verify metrics were added
        assert len(chains.metrics_history) == initial_metrics_count + 2

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
