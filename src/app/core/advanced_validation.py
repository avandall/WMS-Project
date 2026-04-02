"""Advanced input validation using AST parsing and word-boundary regex."""

import re
import ast
import sqlparse
from typing import List, Dict, Any, Optional, Set, Tuple
from app.core.logging import get_logger

logger = get_logger(__name__)

class SQLInjectionValidator:
    """Advanced SQL injection validator using AST and word-boundary patterns."""
    
    # Word-boundary regex patterns for SQL keywords
    SQL_KEYWORD_PATTERNS = {
        # DML keywords
        'SELECT': r'\bSELECT\b',
        'INSERT': r'\bINSERT\b', 
        'UPDATE': r'\bUPDATE\b',
        'DELETE': r'\bDELETE\b',
        'MERGE': r'\bMERGE\b',
        
        # DDL keywords
        'CREATE': r'\bCREATE\b',
        'ALTER': r'\bALTER\b',
        'DROP': r'\bDROP\b',
        'TRUNCATE': r'\bTRUNCATE\b',
        
        # DCL keywords
        'GRANT': r'\bGRANT\b',
        'REVOKE': r'\bREVOKE\b',
        'COMMIT': r'\bCOMMIT\b',
        'ROLLBACK': r'\bROLLBACK\b',
        'SAVEPOINT': r'\bSAVEPOINT\b',
        
        # Utility keywords
        'UNION': r'\bUNION\b',
        'INTERSECT': r'\bINTERSECT\b',
        'EXCEPT': r'\bEXCEPT\b',
        'WITH': r'\bWITH\b',
        
        # Conditional keywords
        'CASE': r'\bCASE\b',
        'WHEN': r'\bWHEN\b',
        'THEN': r'\bTHEN\b',
        'ELSE': r'\bELSE\b',
        'END': r'\bEND\b',
        
        # Function keywords
        'EXEC': r'\bEXEC\b',
        'EXECUTE': r'\bEXECUTE\b',
        'CALL': r'\bCALL\b',
        'CAST': r'\bCAST\b',
        'CONVERT': r'\bCONVERT\b',
        
        # Time-based attack keywords
        'WAITFOR': r'\bWAITFOR\b',
        'DELAY': r'\bDELAY\b',
        'SLEEP': r'\bSLEEP\b',
        'BENCHMARK': r'\bBENCHMARK\b',
        'PG_SLEEP': r'\bPG_SLEEP\b',
        
        # Information schema keywords
        'INFORMATION_SCHEMA': r'\bINFORMATION_SCHEMA\b',
        'SYS': r'\bSYS\b',
        'MASTER': r'\bMASTER\b',
        'MSDB': r'\bMSDB\b',
        
        # File operation keywords
        'BULK': r'\bBULK\b',
        'OPENROWSET': r'\bOPENROWSET\b',
        'OPENDATASOURCE': r'\bOPENDATASOURCE\b',
        'OPENQUERY': r'\bOPENQUERY\b',
    }
    
    # Dangerous function patterns
    DANGEROUS_FUNCTIONS = {
        'XP_CMDShell': r'\bXP_CMDSHELL\b',
        'SP_OACreate': r'\bSP_OACREATE\b',
        'SP_OAMethod': r'\bSP_OAMETHOD\b',
        'LOAD_FILE': r'\bLOAD_FILE\b',
        'INTO_OUTFILE': r'\bINTO_OUTFILE\b',
        'INTO_DUMPFILE': r'\bINTO_DUMPFILE\b',
        'SYSTEM': r'\bSYSTEM\b',
        'EVAL': r'\bEVAL\b',
        'SHELL_EXEC': r'\bSHELL_EXEC\b',
    }
    
    # Comment patterns
    COMMENT_PATTERNS = [
        r'--.*$',  # Single line comment
        r'/\*.*?\*/',  # Multi-line comment
        r'#.*$',  # MySQL style comment
    ]
    
    # String delimiter patterns
    STRING_PATTERNS = [
        r"'[^']*'",  # Single quoted string
        r'"[^"]*"',  # Double quoted string
        r'`[^`]*`',  # Backtick string (MySQL)
    ]
    
    @classmethod
    def validate_with_word_boundaries(cls, input_value: str, field_name: str = "input") -> Tuple[bool, List[str]]:
        """
        Validate input using word-boundary regex patterns.
        Returns (is_valid, list_of_violations)
        """
        violations = []
        
        if not isinstance(input_value, str):
            violations.append(f"{field_name}: Input must be a string")
            return False, violations
        
        # Length validation
        if len(input_value) > 1000:
            violations.append(f"{field_name}: Input too long ({len(input_value)} > 1000)")
        
        # Check for SQL keywords using word-boundary patterns
        input_upper = input_value.upper()
        for keyword, pattern in cls.SQL_KEYWORD_PATTERNS.items():
            if re.search(pattern, input_upper, re.IGNORECASE):
                violations.append(f"{field_name}: Dangerous SQL keyword '{keyword}' detected")
        
        # Check for dangerous functions
        for func_name, pattern in cls.DANGEROUS_FUNCTIONS.items():
            if re.search(pattern, input_upper, re.IGNORECASE):
                violations.append(f"{field_name}: Dangerous function '{func_name}' detected")
        
        # Check for comment patterns
        for pattern in cls.COMMENT_PATTERNS:
            if re.search(pattern, input_value, re.IGNORECASE):
                violations.append(f"{field_name}: SQL comment pattern detected")
        
        # Check for multiple statements
        if ';' in input_value and not cls._is_valid_semicolon_usage(input_value):
            violations.append(f"{field_name}: Multiple SQL statements detected")
        
        return len(violations) == 0, violations
    
    @classmethod
    def _is_valid_semicolon_usage(cls, input_value: str) -> bool:
        """Check if semicolon usage is valid (e.g., in stored procedures)."""
        # Allow semicolons in specific contexts
        valid_contexts = [
            r'END\s*;',  # END of CASE/IF block
            r'BEGIN\s*.*?END\s*;',  # BEGIN...END blocks
            r'CREATE\s+PROCEDURE.*?END\s*;',  # Stored procedures
        ]
        
        for pattern in valid_contexts:
            if re.search(pattern, input_value, re.IGNORECASE | re.DOTALL):
                return True
        
        return False
    
    @classmethod
    def validate_with_ast_parsing(cls, input_value: str, field_name: str = "input") -> Tuple[bool, List[str]]:
        """
        Validate input using AST parsing for code injection detection.
        Returns (is_valid, list_of_violations)
        """
        violations = []
        
        if not isinstance(input_value, str):
            violations.append(f"{field_name}: Input must be a string")
            return False, violations
        
        # Try to parse as Python code to detect code injection
        try:
            tree = ast.parse(input_value)
            
            # Check for dangerous AST nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # Check for function calls
                    if isinstance(node.func, ast.Name):
                        dangerous_functions = ['eval', 'exec', 'compile', '__import__', 'open']
                        if node.func.id in dangerous_functions:
                            violations.append(f"{field_name}: Dangerous function call '{node.func.id}' detected")
                
                elif isinstance(node, ast.Import):
                    violations.append(f"{field_name}: Import statement detected")
                
                elif isinstance(node, ast.ImportFrom):
                    violations.append(f"{field_name}: Import from statement detected")
                
                elif isinstance(node, (ast.Exec, ast.Print)):  # Python 2 compatibility
                    violations.append(f"{field_name}: Dangerous AST node '{type(node).__name__}' detected")
        
        except SyntaxError:
            # Not valid Python code, which is expected for most inputs
            pass
        except Exception as e:
            violations.append(f"{field_name}: AST parsing error - {str(e)}")
        
        return len(violations) == 0, violations
    
    @classmethod
    def validate_sql_structure(cls, sql_query: str, allowed_operations: Set[str] = None) -> Tuple[bool, List[str]]:
        """
        Validate SQL query structure using sqlparse.
        Returns (is_valid, list_of_violations)
        """
        violations = []
        
        if not isinstance(sql_query, str):
            violations.append("SQL query must be a string")
            return False, violations
        
        if allowed_operations is None:
            allowed_operations = {'SELECT'}  # Default to SELECT only
        
        try:
            # Parse the SQL query
            parsed = sqlparse.parse(sql_query)
            
            if not parsed:
                violations.append("Empty or invalid SQL query")
                return False, violations
            
            # Analyze each statement
            for statement in parsed:
                # Get the first token to determine operation type
                tokens = [token for token in statement.flatten() if not token.is_whitespace]
                
                if not tokens:
                    continue
                
                operation = tokens[0].value.upper()
                
                # Check if operation is allowed
                if operation not in allowed_operations:
                    violations.append(f"SQL operation '{operation}' not allowed. Allowed: {allowed_operations}")
                
                # Check for dangerous constructs
                statement_str = str(statement).upper()
                
                # Check for subqueries that might be dangerous
                if re.search(r'\(.*SELECT.*\)', statement_str):
                    violations.append("Subqueries detected - additional review required")
                
                # Check for UNION operations
                if 'UNION' in statement_str and operation != 'SELECT':
                    violations.append("UNION operations in non-SELECT statements")
                
                # Check for function calls
                if re.search(r'\w+\s*\(', statement_str):
                    function_matches = re.findall(r'(\w+)\s*\(', statement_str)
                    dangerous_funcs = ['EXEC', 'EXECUTE', 'SYSTEM', 'SHELL']
                    for func in function_matches:
                        if func in dangerous_funcs:
                            violations.append(f"Dangerous function '{func}' detected")
        
        except Exception as e:
            violations.append(f"SQL parsing error: {str(e)}")
        
        return len(violations) == 0, violations
    
    @classmethod
    def comprehensive_validate(cls, input_value: str, field_name: str = "input", 
                            context: str = "general") -> Tuple[bool, List[str]]:
        """
        Perform comprehensive validation using multiple methods.
        Returns (is_valid, list_of_violations)
        """
        all_violations = []
        
        # Word-boundary regex validation
        regex_valid, regex_violations = cls.validate_with_word_boundaries(input_value, field_name)
        all_violations.extend(regex_violations)
        
        # AST parsing validation (for code injection)
        ast_valid, ast_violations = cls.validate_with_ast_parsing(input_value, field_name)
        all_violations.extend(ast_violations)
        
        # Context-specific validation
        if context == "sql":
            sql_valid, sql_violations = cls.validate_sql_structure(input_value)
            all_violations.extend(sql_violations)
        
        # Additional checks based on context
        if context == "identifier":
            # Check for valid identifier patterns
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', input_value):
                all_violations.append(f"{field_name}: Invalid identifier format")
        
        elif context == "numeric":
            # Check for valid numeric input
            if not re.match(r'^-?\d+(\.\d+)?$', input_value):
                all_violations.append(f"{field_name}: Invalid numeric format")
        
        return len(all_violations) == 0, all_violations

class InputSanitizer:
    """Advanced input sanitization with context-aware processing."""
    
    @staticmethod
    def sanitize_identifier(input_value: str) -> str:
        """Sanitize database identifiers (table names, column names)."""
        if not isinstance(input_value, str):
            return ""
        
        # Remove non-alphanumeric characters except underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '', input_value)
        
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = f"_{sanitized}"
        
        # Truncate to reasonable length
        return sanitized[:64]
    
    @staticmethod
    def sanitize_text_input(input_value: str, max_length: int = 1000) -> str:
        """Sanitize general text input."""
        if not isinstance(input_value, str):
            return ""
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', input_value)
        
        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())
        
        # Remove SQL comment markers
        sanitized = re.sub(r'--.*$', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'/\*.*?\*/', '', sanitized, flags=re.DOTALL)
        sanitized = re.sub(r'#.*$', '', sanitized, flags=re.MULTILINE)
        
        # Truncate to max length
        return sanitized[:max_length]
    
    @staticmethod
    def sanitize_numeric_input(input_value: str) -> str:
        """Sanitize numeric input."""
        if not isinstance(input_value, str):
            return ""
        
        # Keep only digits, decimal point, minus sign, and scientific notation
        sanitized = re.sub(r'[^\d\.\-eE]', '', input_value)
        
        # Validate numeric format
        if not re.match(r'^-?\d+(\.\d+)?([eE][+-]?\d+)?$', sanitized):
            return ""
        
        return sanitized

class SecurityPolicyEnforcer:
    """Enforces security policies on input validation."""
    
    def __init__(self):
        self.validation_rules = {}
        self.sanitization_rules = {}
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default validation and sanitization rules."""
        
        # Validation rules by context
        self.validation_rules = {
            'table_name': {
                'validator': SQLInjectionValidator.validate_with_word_boundaries,
                'max_length': 64,
                'pattern': r'^[a-zA-Z_][a-zA-Z0-9_]*$',
                'context': 'identifier'
            },
            'column_name': {
                'validator': SQLInjectionValidator.validate_with_word_boundaries,
                'max_length': 64,
                'pattern': r'^[a-zA-Z_][a-zA-Z0-9_]*$',
                'context': 'identifier'
            },
            'sql_condition': {
                'validator': SQLInjectionValidator.validate_sql_structure,
                'max_length': 1000,
                'allowed_operations': {'SELECT'},
                'context': 'sql'
            },
            'user_input': {
                'validator': SQLInjectionValidator.comprehensive_validate,
                'max_length': 1000,
                'context': 'general'
            },
            'numeric_value': {
                'validator': SQLInjectionValidator.comprehensive_validate,
                'max_length': 20,
                'context': 'numeric'
            }
        }
        
        # Sanitization rules by context
        self.sanitization_rules = {
            'identifier': InputSanitizer.sanitize_identifier,
            'text': InputSanitizer.sanitize_text_input,
            'numeric': InputSanitizer.sanitize_numeric_input
        }
    
    def validate_input(self, input_value: Any, context: str, field_name: str = "input") -> Tuple[bool, List[str]]:
        """Validate input based on context."""
        if context not in self.validation_rules:
            raise ValueError(f"Unknown validation context: {context}")
        
        rules = self.validation_rules[context]
        violations = []
        
        # Type validation
        if not isinstance(input_value, str):
            violations.append(f"{field_name}: Input must be a string")
            return False, violations
        
        # Length validation
        if 'max_length' in rules and len(input_value) > rules['max_length']:
            violations.append(f"{field_name}: Input too long (max {rules['max_length']})")
        
        # Pattern validation
        if 'pattern' in rules and not re.match(rules['pattern'], input_value):
            violations.append(f"{field_name}: Invalid format")
        
        # Custom validator
        validator = rules['validator']
        if context == 'sql':
            is_valid, validator_violations = validator(input_value, rules.get('allowed_operations'))
        else:
            is_valid, validator_violations = validator(input_value, field_name)
        
        violations.extend(validator_violations)
        
        return len(violations) == 0, violations
    
    def sanitize_input(self, input_value: Any, context: str) -> str:
        """Sanitize input based on context."""
        if context not in self.sanitization_rules:
            raise ValueError(f"Unknown sanitization context: {context}")
        
        sanitizer = self.sanitization_rules[context]
        return sanitizer(input_value)

# Global policy enforcer instance
security_policy = SecurityPolicyEnforcer()
