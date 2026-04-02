"""Secure query builder with parameterized queries and advanced validation."""

import re
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import text
from app.core.logging import get_logger
from app.core.advanced_validation import SQLInjectionValidator, security_policy

logger = get_logger(__name__)

class SecureQueryBuilder:
    """Secure query builder that prevents SQL injection through parameterization and advanced validation."""
    
    def __init__(self, base_table: str):
        # Validate table name using identifier validation
        self.base_table = security_policy.sanitize_input(base_table, "identifier")
        is_valid, violations = security_policy.validate_input(self.base_table, "identifier", "base_table")
        if not is_valid:
            raise ValueError(f"Invalid table name: {'; '.join(violations)}")
        
        self.query_parts = []
        self.parameters = {}
        self.parameter_counter = 0
    
    def select(self, columns: List[str] = None) -> 'SecureQueryBuilder':
        """Add SELECT clause with column validation."""
        if columns is None:
            self.query_parts.append(f"SELECT * FROM {self.base_table}")
        else:
            validated_columns = []
            for i, col in enumerate(columns):
                # Validate each column name
                sanitized_col = security_policy.sanitize_input(col, "identifier")
                is_valid, violations = security_policy.validate_input(sanitized_col, "identifier", f"column_{i}")
                if not is_valid:
                    raise ValueError(f"Invalid column name '{col}': {'; '.join(violations)}")
                validated_columns.append(sanitized_col)
            self.query_parts.append(f"SELECT {', '.join(validated_columns)} FROM {self.base_table}")
        return self
    
    def where(self, condition: str, params: Dict[str, Any] = None) -> 'SecureQueryBuilder':
        """Add WHERE clause with parameterized conditions and validation."""
        if params is None:
            params = {}
        
        # Validate condition template using SQL structure validation
        is_valid, violations = SQLInjectionValidator.validate_sql_structure(
            condition, allowed_operations={'SELECT'}
        )
        if not is_valid:
            raise ValueError(f"Invalid WHERE condition: {'; '.join(violations)}")
        
        # Replace parameter placeholders with named parameters
        param_names = re.findall(r':(\w+)', condition)
        for param_name in param_names:
            if param_name not in params:
                raise ValueError(f"Parameter '{param_name}' not provided in params")
            self.parameters[param_name] = params[param_name]
        
        self.query_parts.append(f"WHERE {condition}")
        return self
    
    def where_equals(self, column: str, value: Any) -> 'SecureQueryBuilder':
        """Add WHERE column = :value clause with validation."""
        # Validate column name
        sanitized_column = security_policy.sanitize_input(column, "identifier")
        is_valid, violations = security_policy.validate_input(sanitized_column, "identifier", "column")
        if not is_valid:
            raise ValueError(f"Invalid column name '{column}': {'; '.join(violations)}")
        
        param_name = f"param_{self.parameter_counter}"
        self.parameter_counter += 1
        
        self.parameters[param_name] = value
        self.query_parts.append(f"WHERE {sanitized_column} = :{param_name}")
        return self
    
    def where_in(self, column: str, values: List[Any]) -> 'SecureQueryBuilder':
        """Add WHERE column IN (:values) clause with validation."""
        # Validate column name
        sanitized_column = security_policy.sanitize_input(column, "identifier")
        is_valid, violations = security_policy.validate_input(sanitized_column, "identifier", "column")
        if not is_valid:
            raise ValueError(f"Invalid column name '{column}': {'; '.join(violations)}")
        
        param_name = f"param_{self.parameter_counter}"
        self.parameter_counter += 1
        
        if not values:
            raise ValueError("IN clause requires at least one value")
        
        # Validate values
        for i, value in enumerate(values):
            if isinstance(value, str):
                is_valid, violations = security_policy.validate_input(value, "user_input", f"in_value_{i}")
                if not is_valid:
                    raise ValueError(f"Invalid IN value: {'; '.join(violations)}")
        
        self.parameters[param_name] = tuple(values)
        self.query_parts.append(f"WHERE {sanitized_column} IN :{param_name}")
        return self
    
    def where_between(self, column: str, start_val: Any, end_val: Any) -> 'SecureQueryBuilder':
        """Add WHERE column BETWEEN :start AND :end clause with validation."""
        # Validate column name
        sanitized_column = security_policy.sanitize_input(column, "identifier")
        is_valid, violations = security_policy.validate_input(sanitized_column, "identifier", "column")
        if not is_valid:
            raise ValueError(f"Invalid column name '{column}': {'; '.join(violations)}")
        
        start_param = f"param_{self.parameter_counter}"
        end_param = f"param_{self.parameter_counter + 1}"
        self.parameter_counter += 2
        
        # Validate numeric values
        if isinstance(start_val, str):
            is_valid, violations = security_policy.validate_input(start_val, "numeric_value", "start_value")
            if not is_valid:
                raise ValueError(f"Invalid start value: {'; '.join(violations)}")
        
        if isinstance(end_val, str):
            is_valid, violations = security_policy.validate_input(end_val, "numeric_value", "end_value")
            if not is_valid:
                raise ValueError(f"Invalid end value: {'; '.join(violations)}")
        
        self.parameters[start_param] = start_val
        self.parameters[end_param] = end_val
        self.query_parts.append(f"WHERE {sanitized_column} BETWEEN :{start_param} AND :{end_param}")
        return self
    
    def join(self, table: str, on_condition: str, join_type: str = "INNER") -> 'SecureQueryBuilder':
        """Add JOIN clause with validation."""
        # Validate table name
        sanitized_table = security_policy.sanitize_input(table, "identifier")
        is_valid, violations = security_policy.validate_input(sanitized_table, "identifier", "join_table")
        if not is_valid:
            raise ValueError(f"Invalid join table '{table}': {'; '.join(violations)}")
        
        # Validate join condition
        is_valid, violations = SQLInjectionValidator.validate_sql_structure(
            on_condition, allowed_operations={'SELECT'}
        )
        if not is_valid:
            raise ValueError(f"Invalid join condition: {'; '.join(violations)}")
        
        if join_type.upper() not in ["INNER", "LEFT", "RIGHT", "FULL", "CROSS"]:
            raise ValueError("Invalid join type")
        
        self.query_parts.append(f"{join_type} JOIN {sanitized_table} ON {on_condition}")
        return self
    
    def order_by(self, column: str, direction: str = "ASC") -> 'SecureQueryBuilder':
        """Add ORDER BY clause with validation."""
        # Validate column name
        sanitized_column = security_policy.sanitize_input(column, "identifier")
        is_valid, violations = security_policy.validate_input(sanitized_column, "identifier", "order_column")
        if not is_valid:
            raise ValueError(f"Invalid order column '{column}': {'; '.join(violations)}")
        
        if direction.upper() not in ["ASC", "DESC"]:
            raise ValueError("Direction must be ASC or DESC")
        
        self.query_parts.append(f"ORDER BY {sanitized_column} {direction}")
        return self
    
    def limit(self, limit: int) -> 'SecureQueryBuilder':
        """Add LIMIT clause with validation."""
        # Validate limit value
        if isinstance(limit, str):
            is_valid, violations = security_policy.validate_input(limit, "numeric_value", "limit")
            if not is_valid:
                raise ValueError(f"Invalid limit value: {'; '.join(violations)}")
            limit = int(limit)
        
        if limit <= 0 or limit > 10000:  # Reasonable limits
            raise ValueError("Limit must be between 1 and 10000")
        
        self.query_parts.append(f"LIMIT {limit}")
        return self
    
    def offset(self, offset: int) -> 'SecureQueryBuilder':
        """Add OFFSET clause with validation."""
        # Validate offset value
        if isinstance(offset, str):
            is_valid, violations = security_policy.validate_input(offset, "numeric_value", "offset")
            if not is_valid:
                raise ValueError(f"Invalid offset value: {'; '.join(violations)}")
            offset = int(offset)
        
        if offset < 0 or offset > 1000000:  # Reasonable limits
            raise ValueError("Offset must be between 0 and 1000000")
        
        self.query_parts.append(f"OFFSET {offset}")
        return self
    
    def build(self) -> Tuple[str, Dict[str, Any]]:
        """Build the final parameterized query."""
        if not self.query_parts:
            raise ValueError("No query parts defined")
        
        query = " ".join(self.query_parts)
        
        # Final validation of the complete query
        is_valid, violations = SQLInjectionValidator.validate_sql_structure(
            query, allowed_operations={'SELECT'}
        )
        if not is_valid:
            raise ValueError(f"Invalid query structure: {'; '.join(violations)}")
        
        logger.debug(f"Built secure query: {query} with params: {self.parameters}")
        return query, self.parameters

class SecureRepository:
    """Base class for secure database operations."""
    
    def __init__(self, session):
        self.session = session
    
    def execute_secure_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a parameterized query securely."""
        try:
            if params is None:
                params = {}
            
            # Validate query string for basic security
            self._validate_query_string(query)
            
            # Execute with parameters
            result = self.session.execute(text(query), params)
            
            # Convert to list of dictionaries
            columns = result.keys()
            rows = result.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
            
        except Exception as e:
            logger.error(f"Secure query execution failed: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Parameters: {params}")
            raise
    
    def execute_secure_scalar(self, query: str, params: Dict[str, Any] = None) -> Any:
        """Execute a parameterized query that returns a single value."""
        try:
            if params is None:
                params = {}
            
            self._validate_query_string(query)
            
            result = self.session.execute(text(query), params)
            return result.scalar()
            
        except Exception as e:
            logger.error(f"Secure scalar query failed: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Parameters: {params}")
            raise
    
    def _validate_query_string(self, query: str) -> None:
        """Validate query string for security issues."""
        # Check for multiple statements
        if ';' in query.lower():
            raise ValueError("Multiple SQL statements not allowed")
        
        # Check for dangerous keywords in non-SELECT queries
        dangerous_keywords = ["drop", "delete", "truncate", "alter", "create", "insert", "update"]
        query_upper = query.upper().strip()
        
        if not query_upper.startswith("SELECT"):
            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    logger.warning(f"Dangerous keyword detected in query: {keyword}")
                    raise ValueError(f"Operation '{keyword}' not allowed in this context")
        
        # Check for comment patterns
        if "--" in query or "/*" in query:
            raise ValueError("SQL comments not allowed in queries")

# Common secure query templates
class SecureQueries:
    """Pre-defined secure query templates."""
    
    @staticmethod
    def get_by_id(table_name: str, id_column: str = "id") -> str:
        """Secure template for getting record by ID."""
        return f"SELECT * FROM {table_name} WHERE {id_column} = :id"
    
    @staticmethod
    def get_with_pagination(table_name: str, where_clause: str = "1=1") -> str:
        """Secure template for paginated results."""
        return f"""
        SELECT * FROM {table_name} 
        WHERE {where_clause} 
        ORDER BY id 
        LIMIT :limit OFFSET :offset
        """
    
    @staticmethod
    def check_exists(table_name: str, where_clause: str) -> str:
        """Secure template for checking record existence."""
        return f"SELECT 1 FROM {table_name} WHERE {where_clause} LIMIT 1"
    
    @staticmethod
    def safe_count(table_name: str, where_clause: str = "1=1") -> str:
        """Secure template for counting records."""
        return f"SELECT COUNT(*) FROM {table_name} WHERE {where_clause}"
    
    @staticmethod
    def safe_delete(table_name: str, id_column: str = "id") -> str:
        """Secure template for deleting record by ID."""
        return f"DELETE FROM {table_name} WHERE {id_column} = :id"
