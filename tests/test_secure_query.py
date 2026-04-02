"""Tests for secure query builder with advanced validation."""

import pytest
from unittest.mock import Mock, patch
from app.core.secure_query import SecureQueryBuilder, SecureRepository
from app.core.advanced_validation import security_policy

class TestSecureQueryBuilder:
    """Test cases for SecureQueryBuilder."""
    
    def test_initialization_with_valid_table(self):
        """Test builder initialization with valid table name."""
        builder = SecureQueryBuilder("products")
        assert builder.base_table == "products"
        assert builder.query_parts == []
        assert builder.parameters == {}
        assert builder.parameter_counter == 0
    
    def test_initialization_with_invalid_table(self):
        """Test builder initialization with invalid table name."""
        invalid_tables = [
            "SELECT",  # SQL keyword
            "products; DROP",  # SQL injection
            "1table",  # Starts with number
            "table-name",  # Contains dash
            "",  # Empty
            None,  # None
        ]
        
        for table_name in invalid_tables:
            with pytest.raises(ValueError, match="Invalid table name"):
                SecureQueryBuilder(table_name)
    
    def test_select_with_default_columns(self):
        """Test SELECT with default columns."""
        builder = SecureQueryBuilder("products")
        builder.select()
        
        assert "SELECT * FROM products" in " ".join(builder.query_parts)
    
    def test_select_with_valid_columns(self):
        """Test SELECT with valid column names."""
        builder = SecureQueryBuilder("products")
        builder.select(["id", "name", "price"])
        
        query_parts = " ".join(builder.query_parts)
        assert "SELECT id, name, price FROM products" in query_parts
    
    def test_select_with_invalid_columns(self):
        """Test SELECT with invalid column names."""
        builder = SecureQueryBuilder("products")
        
        invalid_columns = [
            ["SELECT", "name"],  # SQL keyword
            ["id; DROP", "name"],  # SQL injection
            ["1column", "name"],  # Starts with number
            ["col-name", "name"],  # Contains dash
        ]
        
        for columns in invalid_columns:
            with pytest.raises(ValueError, match="Invalid column name"):
                builder.select(columns)
    
    def test_where_with_valid_condition(self):
        """Test WHERE with valid condition."""
        builder = SecureQueryBuilder("products")
        builder.where("id = :id", {"id": 1})
        
        query_parts = " ".join(builder.query_parts)
        assert "WHERE id = :id" in query_parts
        assert builder.parameters["id"] == 1
    
    def test_where_with_invalid_condition(self):
        """Test WHERE with invalid condition."""
        builder = SecureQueryBuilder("products")
        
        invalid_conditions = [
            "id = 1; DROP TABLE",  # SQL injection
            "SELECT * FROM users",  # Invalid operation
            "INSERT INTO table",  # Invalid operation
        ]
        
        for condition in invalid_conditions:
            with pytest.raises(ValueError, match="Invalid WHERE condition"):
                builder.where(condition, {})
    
    def test_where_with_missing_parameter(self):
        """Test WHERE with missing parameter."""
        builder = SecureQueryBuilder("products")
        
        with pytest.raises(ValueError, match="Parameter .* not provided"):
            builder.where("id = :id AND name = :name", {"id": 1})
    
    def test_where_equals_with_valid_column(self):
        """Test WHERE equals with valid column."""
        builder = SecureQueryBuilder("products")
        builder.where_equals("id", 1)
        
        query_parts = " ".join(builder.query_parts)
        assert "WHERE id = :param_0" in query_parts
        assert builder.parameters["param_0"] == 1
    
    def test_where_equals_with_invalid_column(self):
        """Test WHERE equals with invalid column."""
        builder = SecureQueryBuilder("products")
        
        invalid_columns = ["SELECT", "id; DROP", "1column", "col-name"]
        
        for column in invalid_columns:
            with pytest.raises(ValueError, match="Invalid column name"):
                builder.where_equals(column, 1)
    
    def test_where_in_with_valid_values(self):
        """Test WHERE IN with valid values."""
        builder = SecureQueryBuilder("products")
        builder.where_in("id", [1, 2, 3])
        
        query_parts = " ".join(builder.query_parts)
        assert "WHERE id IN :param_0" in query_parts
        assert builder.parameters["param_0"] == (1, 2, 3)
    
    def test_where_in_with_empty_values(self):
        """Test WHERE IN with empty values."""
        builder = SecureQueryBuilder("products")
        
        with pytest.raises(ValueError, match="IN clause requires at least one value"):
            builder.where_in("id", [])
    
    def test_where_in_with_invalid_values(self):
        """Test WHERE IN with invalid values."""
        builder = SecureQueryBuilder("products")
        
        with pytest.raises(ValueError, match="Invalid IN value"):
            builder.where_in("id", ["SELECT", "name"])
    
    def test_where_between_with_valid_values(self):
        """Test WHERE BETWEEN with valid values."""
        builder = SecureQueryBuilder("products")
        builder.where_between("price", 10.0, 100.0)
        
        query_parts = " ".join(builder.query_parts)
        assert "WHERE price BETWEEN :param_0 AND :param_1" in query_parts
        assert builder.parameters["param_0"] == 10.0
        assert builder.parameters["param_1"] == 100.0
    
    def test_where_between_with_invalid_values(self):
        """Test WHERE BETWEEN with invalid values."""
        builder = SecureQueryBuilder("products")
        
        with pytest.raises(ValueError, match="Invalid start value"):
            builder.where_between("price", "SELECT", 100.0)
        
        with pytest.raises(ValueError, match="Invalid end value"):
            builder.where_between("price", 10.0, "DROP")
    
    def test_join_with_valid_table_and_condition(self):
        """Test JOIN with valid table and condition."""
        builder = SecureQueryBuilder("products")
        builder.join("categories", "products.category_id = categories.id")
        
        query_parts = " ".join(builder.query_parts)
        assert "INNER JOIN categories ON products.category_id = categories.id" in query_parts
    
    def test_join_with_invalid_table(self):
        """Test JOIN with invalid table name."""
        builder = SecureQueryBuilder("products")
        
        with pytest.raises(ValueError, match="Invalid join table"):
            builder.join("SELECT", "condition")
    
    def test_join_with_invalid_condition(self):
        """Test JOIN with invalid condition."""
        builder = SecureQueryBuilder("products")
        
        with pytest.raises(ValueError, match="Invalid join condition"):
            builder.join("categories", "DROP TABLE")
    
    def test_join_with_invalid_type(self):
        """Test JOIN with invalid join type."""
        builder = SecureQueryBuilder("products")
        
        with pytest.raises(ValueError, match="Invalid join type"):
            builder.join("categories", "condition", "INVALID")
    
    def test_order_by_with_valid_column(self):
        """Test ORDER BY with valid column."""
        builder = SecureQueryBuilder("products")
        builder.order_by("name", "ASC")
        
        query_parts = " ".join(builder.query_parts)
        assert "ORDER BY name ASC" in query_parts
    
    def test_order_by_with_invalid_column(self):
        """Test ORDER BY with invalid column."""
        builder = SecureQueryBuilder("products")
        
        with pytest.raises(ValueError, match="Invalid order column"):
            builder.order_by("SELECT", "ASC")
    
    def test_order_by_with_invalid_direction(self):
        """Test ORDER BY with invalid direction."""
        builder = SecureQueryBuilder("products")
        
        with pytest.raises(ValueError, match="Direction must be ASC or DESC"):
            builder.order_by("name", "INVALID")
    
    def test_limit_with_valid_value(self):
        """Test LIMIT with valid value."""
        builder = SecureQueryBuilder("products")
        builder.limit(10)
        
        query_parts = " ".join(builder.query_parts)
        assert "LIMIT 10" in query_parts
    
    def test_limit_with_invalid_value(self):
        """Test LIMIT with invalid values."""
        builder = SecureQueryBuilder("products")
        
        invalid_limits = [0, -1, 10001, "SELECT", "abc"]
        
        for limit in invalid_limits:
            with pytest.raises(ValueError):
                builder.limit(limit)
    
    def test_offset_with_valid_value(self):
        """Test OFFSET with valid value."""
        builder = SecureQueryBuilder("products")
        builder.offset(20)
        
        query_parts = " ".join(builder.query_parts)
        assert "OFFSET 20" in query_parts
    
    def test_offset_with_invalid_value(self):
        """Test OFFSET with invalid values."""
        builder = SecureQueryBuilder("products")
        
        invalid_offsets = [-1, 1000001, "SELECT", "abc"]
        
        for offset in invalid_offsets:
            with pytest.raises(ValueError):
                builder.offset(offset)
    
    def test_build_valid_query(self):
        """Test building a valid query."""
        builder = SecureQueryBuilder("products")
        query, params = builder.select(["id", "name"]).where("price > :min_price", {"min_price": 10}).limit(5).build()
        
        assert "SELECT id, name FROM products" in query
        assert "WHERE price > :min_price" in query
        assert "LIMIT 5" in query
        assert params["min_price"] == 10
    
    def test_build_empty_query(self):
        """Test building query with no parts."""
        builder = SecureQueryBuilder("products")
        
        with pytest.raises(ValueError, match="No query parts defined"):
            builder.build()
    
    def test_build_invalid_query_structure(self):
        """Test building query with invalid structure."""
        builder = SecureQueryBuilder("products")
        builder.where("1=1; DROP TABLE", {})
        
        with pytest.raises(ValueError, match="Invalid query structure"):
            builder.build()

class TestSecureQueryBuilderComplexQueries:
    """Test complex query scenarios."""
    
    def test_complex_select_query(self):
        """Test building a complex SELECT query."""
        builder = SecureQueryBuilder("products")
        
        query, params = builder \
            .select(["id", "name", "price"]) \
            .where("price BETWEEN :min AND :max", {"min": 10, "max": 100}) \
            .where_in("category_id", [1, 2, 3]) \
            .order_by("name", "ASC") \
            .limit(10) \
            .offset(20) \
            .build()
        
        expected_parts = [
            "SELECT id, name, price FROM products",
            "WHERE price BETWEEN :min AND :max",
            "WHERE category_id IN :param_0",
            "ORDER BY name ASC",
            "LIMIT 10",
            "OFFSET 20"
        ]
        
        for part in expected_parts:
            assert part in query
        
        assert params["min"] == 10
        assert params["max"] == 100
        assert params["param_0"] == (1, 2, 3)
    
    def test_query_with_joins(self):
        """Test query with JOIN operations."""
        builder = SecureQueryBuilder("products")
        
        query, params = builder \
            .select(["p.id", "p.name", "c.name as category"]) \
            .join("categories", "p.category_id = c.id") \
            .where("p.price > :min_price", {"min_price": 50}) \
            .order_by("p.name", "ASC") \
            .build()
        
        assert "SELECT p.id, p.name, c.name as category FROM products" in query
        assert "INNER JOIN categories ON p.category_id = c.id" in query
        assert "WHERE p.price > :min_price" in query
        assert "ORDER BY p.name ASC" in query
        assert params["min_price"] == 50
    
    def test_left_join_query(self):
        """Test LEFT JOIN query."""
        builder = SecureQueryBuilder("products")
        
        query, params = builder \
            .select(["p.id", "p.name", "i.quantity"]) \
            .join("inventory", "p.id = i.product_id", "LEFT") \
            .where("p.active = :active", {"active": True}) \
            .build()
        
        assert "LEFT JOIN inventory ON p.id = i.product_id" in query
        assert "WHERE p.active = :active" in query
        assert params["active"] == True
    
    def test_multiple_where_conditions(self):
        """Test multiple WHERE conditions."""
        builder = SecureQueryBuilder("products")
        
        query, params = builder \
            .where("price > :min_price", {"min_price": 10}) \
            .where("category_id = :category_id", {"category_id": 1}) \
            .where("active = :active", {"active": True}) \
            .build()
        
        # Should have multiple WHERE clauses (this would need to be handled in real implementation)
        assert query.count("WHERE") >= 3
        assert params["min_price"] == 10
        assert params["category_id"] == 1
        assert params["active"] == True

class TestSecureRepository:
    """Test cases for SecureRepository."""
    
    def test_execute_secure_query_success(self):
        """Test successful secure query execution."""
        # Mock session
        mock_session = Mock()
        mock_result = Mock()
        mock_result.keys.return_value = ["id", "name"]
        mock_result.fetchall.return_value = [
            (1, "Product 1"),
            (2, "Product 2")
        ]
        mock_session.execute.return_value = mock_result
        
        repo = SecureRepository(mock_session)
        
        query = "SELECT id, name FROM products WHERE price > :min_price"
        params = {"min_price": 10}
        
        results = repo.execute_secure_query(query, params)
        
        expected = [
            {"id": 1, "name": "Product 1"},
            {"id": 2, "name": "Product 2"}
        ]
        
        assert results == expected
        mock_session.execute.assert_called_once()
    
    def test_execute_secure_query_with_validation(self):
        """Test secure query execution with validation."""
        mock_session = Mock()
        mock_result = Mock()
        mock_result.keys.return_value = ["id", "name"]
        mock_result.fetchall.return_value = []
        mock_session.execute.return_value = mock_result
        
        repo = SecureRepository(mock_session)
        
        # Test with dangerous query
        dangerous_query = "SELECT * FROM users; DROP TABLE users;"
        
        with pytest.raises(ValueError, match="dangerous keyword"):
            repo.execute_secure_query(dangerous_query)
    
    def test_execute_secure_scalar_success(self):
        """Test successful scalar query execution."""
        mock_session = Mock()
        mock_result = Mock()
        mock_result.scalar.return_value = 42
        mock_session.execute.return_value = mock_result
        
        repo = SecureRepository(mock_session)
        
        query = "SELECT COUNT(*) FROM products"
        result = repo.execute_secure_scalar(query)
        
        assert result == 42
        mock_session.execute.assert_called_once()
    
    def test_query_string_validation(self):
        """Test query string validation."""
        mock_session = Mock()
        repo = SecureRepository(mock_session)
        
        # Test dangerous queries
        dangerous_queries = [
            "SELECT * FROM users; DROP TABLE users;",
            "INSERT INTO table VALUES (1)",
            "UPDATE table SET col = 1",
            "DELETE FROM table WHERE id = 1",
            "SELECT * FROM table -- comment",
            "SELECT * FROM table /* comment */",
        ]
        
        for query in dangerous_queries:
            with pytest.raises(ValueError):
                repo._validate_query_string(query)
        
        # Test safe queries
        safe_queries = [
            "SELECT * FROM users WHERE id = :id",
            "SELECT COUNT(*) FROM products",
            "SELECT name, price FROM products ORDER BY name",
        ]
        
        for query in safe_queries:
            # Should not raise exception
            repo._validate_query_string(query)

class TestIntegration:
    """Integration tests for the complete validation system."""
    
    def test_end_to_end_query_building(self):
        """Test end-to-end query building with validation."""
        builder = SecureQueryBuilder("products")
        
        # Build a complex query
        query, params = builder \
            .select(["id", "name", "price", "category_id"]) \
            .where("price > :min_price AND price < :max_price", {"min_price": 10, "max_price": 100}) \
            .where_in("category_id", [1, 2, 3, 4, 5]) \
            .join("categories", "products.category_id = categories.id", "LEFT") \
            .order_by("name", "ASC") \
            .limit(25) \
            .offset(50) \
            .build()
        
        # Verify query structure
        assert "SELECT id, name, price, category_id FROM products" in query
        assert "WHERE price > :min_price AND price < :max_price" in query
        assert "WHERE category_id IN :param_0" in query
        assert "LEFT JOIN categories ON products.category_id = categories.id" in query
        assert "ORDER BY name ASC" in query
        assert "LIMIT 25" in query
        assert "OFFSET 50" in query
        
        # Verify parameters
        assert params["min_price"] == 10
        assert params["max_price"] == 100
        assert params["param_0"] == (1, 2, 3, 4, 5)
    
    def test_security_policy_integration(self):
        """Test integration with security policy."""
        # Test that all validation goes through the security policy
        builder = SecureQueryBuilder("products")
        
        # This should work
        builder.select(["id", "name"])
        
        # This should fail through security policy validation
        with pytest.raises(ValueError):
            builder.select(["SELECT", "name"])
    
    def test_parameter_isolation(self):
        """Test that parameters are properly isolated."""
        builder1 = SecureQueryBuilder("products")
        builder2 = SecureQueryBuilder("categories")
        
        builder1.where_equals("id", 1)
        builder2.where_equals("id", 2)
        
        # Parameters should be separate
        assert builder1.parameters["param_0"] == 1
        assert builder2.parameters["param_0"] == 2
        assert builder1.parameter_counter == 1
        assert builder2.parameter_counter == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
