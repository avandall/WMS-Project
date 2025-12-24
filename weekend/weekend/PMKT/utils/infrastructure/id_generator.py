"""
ID generation utilities for PMKT services.
Provides stateless ID generation for various entities.
"""

import threading
from typing import Callable


class IDGenerator:
    """Thread-safe ID generator for stateless services."""

    _generators = {}
    _lock = threading.Lock()

    @staticmethod
    def get_generator(name: str, start_id: int = 1) -> Callable[[], int]:
        """Get or create a named ID generator."""
        with IDGenerator._lock:
            if name not in IDGenerator._generators:
                IDGenerator._generators[name] = _ThreadSafeCounter(start_id)
            return IDGenerator._generators[name].next_id

    @staticmethod
    def reset_generator(name: str, start_id: int = 1) -> None:
        """Reset a named generator to start from a specific ID."""
        with IDGenerator._lock:
            IDGenerator._generators[name] = _ThreadSafeCounter(start_id)


class _ThreadSafeCounter:
    """Thread-safe counter for ID generation."""

    def __init__(self, start: int = 1):
        self._counter = start - 1
        self._lock = threading.Lock()

    def next_id(self) -> int:
        with self._lock:
            self._counter += 1
            return self._counter


# Convenience functions for common generators
def document_id_generator() -> Callable[[], int]:
    """Get document ID generator."""
    return IDGenerator.get_generator("document", 1)

def warehouse_id_generator() -> Callable[[], int]:
    """Get warehouse ID generator."""
    return IDGenerator.get_generator("warehouse", 1)

def product_id_generator() -> Callable[[], int]:
    """Get product ID generator."""
    return IDGenerator.get_generator("product", 1)