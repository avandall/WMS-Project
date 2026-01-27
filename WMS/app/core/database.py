"""
Database configuration for PMKT Warehouse Management System.
Provides SQLAlchemy engine, session factory, and base class.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool
import time
from app.core.settings import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Production-grade connection pool configuration
engine = create_engine(
    settings.database_url,
    future=True,
    echo=settings.debug,  # Only log SQL in debug mode
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=settings.db_pool_size,  # Connection pool size
    max_overflow=settings.db_max_overflow,  # Additional connections when pool exhausted
    pool_timeout=settings.db_pool_timeout,  # Wait time for connection
    pool_recycle=settings.db_pool_recycle,  # Recycle connections after N seconds
    poolclass=QueuePool,  # Production-grade pool
    connect_args={
        "connect_timeout": 10,  # PostgreSQL connection timeout
        "options": "-c statement_timeout=30000",  # 30 second query timeout
    } if "postgresql" in settings.database_url else {},
)

# Listen for connection events to log pool statistics
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    logger.debug("Database connection established")

@event.listens_for(engine, "close")
def receive_close(dbapi_conn, connection_record):
    logger.debug("Database connection closed")


@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.perf_counter()


@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    if hasattr(context, "_query_start_time"):
        elapsed_ms = (time.perf_counter() - context._query_start_time) * 1000
        if elapsed_ms > 200:
            logger.warning(f"Slow query ({elapsed_ms:.1f} ms): {statement}")
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_session():
    """Yield a database session scoped to the request."""
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Ensure any pending changes are committed
    except Exception as e:
        logger.error(f"Database session error: {type(e).__name__}: {str(e)}")
        db.rollback()
        raise
    finally:
        db.expunge_all()  # Detach all objects to prevent DetachedInstanceError
        db.close()


def init_db() -> None:
    """Create database tables if they do not exist."""
    try:
        # Import models to ensure they are registered with SQLAlchemy metadata
        from app.repositories.sql import models  # noqa: F401

        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


def check_db_connection() -> bool:
    """Check if database connection is healthy."""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False
