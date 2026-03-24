"""
Transaction management for ensuring ACID properties.
Provides context manager for multi-repository operations.
"""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session
from app.core.logging import get_logger

logger = get_logger(__name__)


@contextmanager
def transaction_scope(session: Session) -> Generator[Session, None, None]:
    """
    Provide a transactional scope around a series of operations.
    
    Automatically commits on success and rolls back on failure.
    Ensures atomicity across multiple repository operations.
    
    Usage:
        with transaction_scope(session) as tx_session:
            repo1.save(entity1)
            repo2.update(entity2)
            # All commits or all rollback
    
    Args:
        session: SQLAlchemy session
        
    Yields:
        Transaction-scoped session
        
    Raises:
        Any exception from operations (after rollback)
    """
    try:
        logger.debug("Transaction started")
        yield session
        session.commit()
        logger.debug("Transaction committed successfully")
    except Exception as e:
        logger.error(f"Transaction failed, rolling back: {type(e).__name__}: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()


class TransactionalRepository:
    """
    Base class for repositories that support transactional operations.
    Allows disabling auto-commit for batch operations.
    """
    
    def __init__(self, session: Session):
        self.session = session
        self._auto_commit = True
    
    def set_auto_commit(self, enabled: bool) -> None:
        """
        Enable or disable automatic commits.
        
        When disabled, caller must manually commit.
        Useful for multi-step transactional operations.
        
        Args:
            enabled: Whether to auto-commit after operations
        """
        self._auto_commit = enabled
        logger.debug(f"Auto-commit set to: {enabled}")
    
    def _commit_if_auto(self) -> None:
        """Commit only if auto-commit is enabled."""
        if self._auto_commit:
            self.session.commit()
            logger.debug("Auto-committed transaction")
