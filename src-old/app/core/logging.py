"""
Centralized logging configuration for PMKT WMS.
Provides structured logging with context tracking.
"""

import logging
import sys
from typing import Optional
from contextvars import ContextVar

# Context variable for request tracking
request_id_ctx: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class ContextualFormatter(logging.Formatter):
    """Custom formatter that includes request ID in logs."""

    def format(self, record):
        request_id = request_id_ctx.get()
        if request_id:
            record.request_id = request_id
        else:
            record.request_id = 'N/A'
        return super().format(record)


def setup_logging(level: str = "INFO") -> None:
    """
    Configure application-wide logging with structured format.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_format = (
        "%(asctime)s | %(levelname)-8s | [%(request_id)s] | "
        "%(name)s:%(funcName)s:%(lineno)d | %(message)s"
    )
    
    formatter = ContextualFormatter(
        log_format,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.addHandler(console_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def set_request_id(request_id: str) -> None:
    """Set request ID in context for log correlation."""
    request_id_ctx.set(request_id)


def clear_request_id() -> None:
    """Clear request ID from context."""
    request_id_ctx.set(None)
