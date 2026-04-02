"""Secure database configuration with hardening measures."""

import os
import time
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool
from app.core.settings import settings
from app.core.logging import get_logger
from app.core.advanced_validation import SQLInjectionValidator, security_policy

logger = get_logger(__name__)

def validate_sql_input(input_value: str, field_name: str = "input") -> bool:
    """
    Validate input using advanced SQL injection detection.
    Returns True if safe, False if potentially malicious.
    """
    if not isinstance(input_value, str):
        return False
    
    # Use comprehensive validation with word-boundary regex and AST parsing
    is_valid, violations = SQLInjectionValidator.comprehensive_validate(
        input_value, field_name, context="general"
    )
    
    if not is_valid:
        logger.warning(f"SQL injection validation failed for {field_name}: {violations}")
        return False
    
    return True

def sanitize_input(input_value: str) -> str:
    """
    Sanitize input using context-aware sanitization.
    This is a fallback defense, not a replacement for validation.
    """
    if not isinstance(input_value, str):
        return ""
    
    return security_policy.sanitize_input(input_value, "text")

class SecureQueryValidator:
    """Validates and sanitizes query parameters using advanced validation."""
    
    @staticmethod
    def validate_id(id_value: Any, field_name: str = "id") -> int:
        """Validate ID parameters."""
        try:
            if isinstance(id_value, str):
                # Validate string input first
                is_valid, violations = security_policy.validate_input(id_value, "numeric_value", field_name)
                if not is_valid:
                    raise ValueError(f"Invalid {field_name}: {'; '.join(violations)}")
                id_value = int(id_value)
            elif not isinstance(id_value, int):
                raise ValueError(f"{field_name} must be an integer")
            
            if id_value <= 0 or id_value > 2**31:  # Reasonable limit
                raise ValueError(f"{field_name} out of valid range")
            
            return id_value
        except (ValueError, TypeError):
            raise ValueError(f"Invalid {field_name} format")
    
    @staticmethod
    def validate_text_input(text_value: Any, field_name: str, max_length: int = 255) -> str:
        """Validate text input parameters."""
        if text_value is None:
            return ""
        
        if not isinstance(text_value, str):
            raise ValueError(f"{field_name} must be a string")
        
        # Use advanced validation
        is_valid, violations = security_policy.validate_input(text_value, "user_input", field_name)
        if not is_valid:
            raise ValueError(f"Invalid {field_name}: {'; '.join(violations)}")
        
        # Apply sanitization as additional defense
        text_value = sanitize_input(text_value.strip())
        
        if len(text_value) > max_length:
            raise ValueError(f"{field_name} too long (max {max_length} characters)")
        
        return text_value
    
    @staticmethod
    def validate_identifier(identifier_value: Any, field_name: str, max_length: int = 64) -> str:
        """Validate database identifiers (table names, column names)."""
        if identifier_value is None:
            raise ValueError(f"{field_name} cannot be None")
        
        if not isinstance(identifier_value, str):
            raise ValueError(f"{field_name} must be a string")
        
        # Use identifier validation
        is_valid, violations = security_policy.validate_input(identifier_value, "identifier", field_name)
        if not is_valid:
            raise ValueError(f"Invalid {field_name}: {'; '.join(violations)}")
        
        # Apply identifier sanitization
        sanitized = security_policy.sanitize_input(identifier_value, "identifier")
        
        if len(sanitized) > max_length:
            raise ValueError(f"{field_name} too long (max {max_length} characters)")
        
        return sanitized
    
    @staticmethod
    def validate_numeric_input(num_value: Any, field_name: str, min_val: float = 0, max_val: float = None) -> float:
        """Validate numeric input parameters."""
        try:
            if isinstance(num_value, str):
                # Validate string numeric input
                is_valid, violations = security_policy.validate_input(num_value, "numeric_value", field_name)
                if not is_valid:
                    raise ValueError(f"Invalid {field_name}: {'; '.join(violations)}")
                num_value = float(num_value)
            elif not isinstance(num_value, (int, float)):
                raise ValueError(f"{field_name} must be a number")
            else:
                num_value = float(num_value)
            
            if num_value < min_val:
                raise ValueError(f"{field_name} must be at least {min_val}")
            
            if max_val is not None and num_value > max_val:
                raise ValueError(f"{field_name} must be at most {max_val}")
            
            return num_value
        except (ValueError, TypeError):
            raise ValueError(f"Invalid {field_name} format")

class SecureDatabaseConfig:
    """Hardened database configuration."""
    
    @staticmethod
    def get_readonly_engine() -> Any:
        """Get read-only replica database engine."""
        readonly_url = os.getenv("READONLY_DATABASE_URL", settings.database_url)
        
        return create_engine(
            readonly_url,
            future=True,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_size=5,  # Smaller pool for read operations
            max_overflow=2,
            pool_timeout=settings.db_pool_timeout,
            pool_recycle=settings.db_pool_recycle,
            poolclass=QueuePool,
            connect_args={
                "connect_timeout": 10,
                "options": "-c statement_timeout=10000",  # 10 second timeout
                "application_name": "wms_readonly",
                # Read-only settings
                "default_transaction_isolation": "READ COMMITTED",
                "readonly": True,
            }
            if "postgresql" in readonly_url else {}
        )
    
    @staticmethod
    def get_restricted_engine() -> Any:
        """Get restricted database engine for write operations."""
        # Use restricted user if available
        restricted_url = os.getenv("RESTRICTED_DATABASE_URL", settings.database_url)
        
        return create_engine(
            restricted_url,
            future=True,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_size=min(settings.db_pool_size, 10),  # Limit pool size
            max_overflow=2,
            pool_timeout=settings.db_pool_timeout,
            pool_recycle=settings.db_pool_recycle,
            poolclass=QueuePool,
            connect_args={
                "connect_timeout": 5,  # Shorter timeout for security
                "options": "-c statement_timeout=5000",  # 5 second timeout
                "application_name": "wms_restricted",
                # Security restrictions
                "default_transaction_isolation": "READ COMMITTED",
                "tcp_keepalives_idle": 1,
                "tcp_keepalives_interval": 10,
                # Connection limits
                "max_prepared_statements": 10,
            }
            if "postgresql" in restricted_url else {}
        )
    
    @staticmethod
    def get_admin_engine() -> Any:
        """Get admin database engine for maintenance operations."""
        admin_url = os.getenv("ADMIN_DATABASE_URL", settings.database_url)
        
        return create_engine(
            admin_url,
            future=True,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_size=2,  # Very limited pool for admin operations
            max_overflow=1,
            pool_timeout=settings.db_pool_timeout,
            pool_recycle=settings.db_pool_recycle,
            poolclass=QueuePool,
            connect_args={
                "connect_timeout": 15,
                "options": "-c statement_timeout=60000",  # 60 second timeout for admin
                "application_name": "wms_admin",
            }
            if "postgresql" in admin_url else {}
        )

# Create engines
readonly_engine = SecureDatabaseConfig.get_readonly_engine()
restricted_engine = SecureDatabaseConfig.get_restricted_engine()
admin_engine = SecureDatabaseConfig.get_admin_engine()

# Session factories
ReadonlySessionLocal = sessionmaker(bind=readonly_engine, autoflush=False, autocommit=False, future=True)
RestrictedSessionLocal = sessionmaker(bind=restricted_engine, autoflush=False, autocommit=False, future=True)
AdminSessionLocal = sessionmaker(bind=admin_engine, autoflush=False, autocommit=False, future=True)

Base = declarative_base()

# Event listeners for query monitoring
@event.listens_for(restricted_engine, "before_cursor_execute")
def restricted_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Monitor and validate queries on restricted engine."""
    context._query_start_time = time.perf_counter()
    
    # Log query for monitoring
    logger.info(f"RESTRICTED_QUERY: {statement[:200]}... PARAMS: {str(parameters)[:100]}")
    
    # Check for suspicious patterns
    statement_upper = statement.upper()
    suspicious_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "INSERT", "UPDATE"]
    
    for keyword in suspicious_keywords:
        if keyword in statement_upper and "SELECT" not in statement_upper:
            logger.warning(f"Suspicious operation detected: {keyword} in query: {statement[:100]}...")

@event.listens_for(restricted_engine, "after_cursor_execute")
def restricted_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Monitor query execution time on restricted engine."""
    if hasattr(context, "_query_start_time"):
        elapsed_ms = (time.perf_counter() - context._query_start_time) * 1000
        if elapsed_ms > 5000:  # 5 second threshold
            logger.warning(f"Slow restricted query ({elapsed_ms:.1f} ms): {statement[:100]}...")

@event.listens_for(readonly_engine, "before_cursor_execute")
def readonly_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Monitor queries on read-only engine."""
    context._query_start_time = time.perf_counter()
    
    # Ensure no write operations
    write_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "TRUNCATE"]
    statement_upper = statement.upper()
    
    for keyword in write_keywords:
        if keyword in statement_upper:
            logger.error(f"Write operation attempted on read-only engine: {keyword} in: {statement[:100]}...")
            raise Exception(f"Write operations not allowed on read-only connection")

def get_readonly_session():
    """Get read-only database session."""
    db = ReadonlySessionLocal()
    try:
        yield db
        # No commits needed for read-only
    except Exception as e:
        logger.error(f"Read-only session error: {type(e).__name__}: {str(e)}")
        raise
    finally:
        db.expunge_all()
        db.close()

def get_restricted_session():
    """Get restricted database session."""
    db = RestrictedSessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Restricted session error: {type(e).__name__}: {str(e)}")
        db.rollback()
        raise
    finally:
        db.expunge_all()
        db.close()

def get_admin_session():
    """Get admin database session."""
    db = AdminSessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Admin session error: {type(e).__name__}: {str(e)}")
        db.rollback()
        raise
    finally:
        db.expunge_all()
        db.close()

def check_connection_health() -> bool:
    """Check health of all database connections."""
    engines_status = {}
    
    for name, engine in [("readonly", readonly_engine), ("restricted", restricted_engine), ("admin", admin_engine)]:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                engines_status[name] = "healthy"
        except Exception as e:
            logger.error(f"{name} engine health check failed: {str(e)}")
            engines_status[name] = "unhealthy"
    
    logger.info(f"Database engine health status: {engines_status}")
    return all(status == "healthy" for status in engines_status.values())
