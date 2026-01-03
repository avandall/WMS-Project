"""
Database configuration for PMKT Warehouse Management System.
Provides SQLAlchemy engine, session factory, and base class.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.settings import settings

# Create engine with PostgreSQL-specific settings
engine = create_engine(
    settings.database_url,
    future=True,
    echo=False,
    pool_pre_ping=True,  # Verify connections before using them
    poolclass=NullPool if "sqlite" in settings.database_url else None,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_session():
    """Yield a database session scoped to the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create database tables if they do not exist."""
    # Import models to ensure they are registered with SQLAlchemy metadata
    from app.repositories.sql import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
