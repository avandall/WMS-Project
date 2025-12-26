"""
Application utilities for PMKT.
Contains use case helpers and application-level utilities.
"""

from typing import Any, Dict, List, Optional, TypeVar, Generic
from dataclasses import dataclass
from app.exceptions.business_exceptions import ApplicationError

T = TypeVar('T')


@dataclass
class PaginatedResult(Generic[T]):
    """Generic paginated result container."""
    items: List[T]
    total_count: int
    page: int
    page_size: int
    total_pages: int

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1


class PaginationUtils:
    """Utility class for pagination operations."""

    @staticmethod
    def paginate_list(items: List[T], page: int = 1, page_size: int = 10) -> PaginatedResult[T]:
        """Paginate a list of items."""
        if page < 1:
            raise ApplicationError("Page must be greater than 0")
        if page_size < 1:
            raise ApplicationError("Page size must be greater than 0")

        total_count = len(items)
        total_pages = (total_count + page_size - 1) // page_size

        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        paginated_items = items[start_index:end_index]

        return PaginatedResult(
            items=paginated_items,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    @staticmethod
    def validate_pagination_params(page: int, page_size: int, max_page_size: int = 100) -> None:
        """Validate pagination parameters."""
        if page < 1:
            raise ApplicationError("Page must be >= 1")
        if page_size < 1 or page_size > max_page_size:
            raise ApplicationError(f"Page size must be between 1 and {max_page_size}")


class SortingUtils:
    """Utility class for sorting operations."""

    @staticmethod
    def sort_by_field(items: List[Dict[str, Any]], field: str, reverse: bool = False) -> List[Dict[str, Any]]:
        """Sort a list of dictionaries by a field."""
        return sorted(items, key=lambda x: x.get(field, ''), reverse=reverse)

    @staticmethod
    def sort_by_attribute(items: List[T], attribute: str, reverse: bool = False) -> List[T]:
        """Sort a list of objects by an attribute."""
        return sorted(items, key=lambda x: getattr(x, attribute, ''), reverse=reverse)


class FilterUtils:
    """Utility class for filtering operations."""

    @staticmethod
    def filter_by_field(items: List[Dict[str, Any]], field: str, value: Any) -> List[Dict[str, Any]]:
        """Filter a list of dictionaries by field value."""
        return [item for item in items if item.get(field) == value]

    @staticmethod
    def filter_by_condition(items: List[T], condition_func) -> List[T]:
        """Filter items using a condition function."""
        return [item for item in items if condition_func(item)]


class SearchUtils:
    """Utility class for search operations."""

    @staticmethod
    def search_text(items: List[Dict[str, Any]], search_field: str, query: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Search for text in a specific field."""
        if not case_sensitive:
            query = query.lower()

        def matches(item):
            value = str(item.get(search_field, ''))
            if not case_sensitive:
                value = value.lower()
            return query in value

        return [item for item in items if matches(item)]

    @staticmethod
    def search_multiple_fields(items: List[Dict[str, Any]], fields: List[str], query: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Search for text across multiple fields."""
        if not case_sensitive:
            query = query.lower()

        def matches(item):
            for field in fields:
                value = str(item.get(field, ''))
                if not case_sensitive:
                    value = value.lower()
                if query in value:
                    return True
            return False

        return [item for item in items if matches(item)]


__all__ = [
    'PaginatedResult',
    'PaginationUtils',
    'SortingUtils',
    'FilterUtils',
    'SearchUtils'
]