"""
Domain utilities for PMKT.
Contains business logic helpers and validation utilities.
"""

from typing import Any, Dict, List
from datetime import datetime, date
from app.exceptions.business_exceptions import ValidationError, BusinessRuleViolationError


class ValidationUtils:
    """Utility class for common validation operations."""

    @staticmethod
    def validate_positive_integer(value: int, field_name: str) -> None:
        """Validate that a value is a positive integer."""
        if not isinstance(value, int) or value <= 0:
            raise ValidationError(f"{field_name} must be a positive integer")

    @staticmethod
    def validate_string_length(value: str, field_name: str, min_length: int = 1, max_length: int = None) -> None:
        """Validate string length constraints."""
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string")

        if len(value.strip()) < min_length:
            raise ValidationError(f"{field_name} cannot be empty")

        if max_length and len(value) > max_length:
            raise ValidationError(f"{field_name} cannot exceed {max_length} characters")

    @staticmethod
    def validate_positive_float(value: float, field_name: str) -> None:
        """Validate that a value is a positive float."""
        if not isinstance(value, (int, float)) or value < 0:
            raise ValidationError(f"{field_name} must be a non-negative number")

    @staticmethod
    def validate_date_range(start_date: date, end_date: date, field_name: str = "date range") -> None:
        """Validate that start_date is before or equal to end_date."""
        if start_date > end_date:
            raise ValidationError(f"{field_name}: start date cannot be after end date")


class BusinessRulesUtils:
    """Utility class for common business rule validations."""

    @staticmethod
    def validate_warehouse_transfer(from_warehouse_id: int, to_warehouse_id: int) -> None:
        """Validate warehouse transfer business rules."""
        if from_warehouse_id == to_warehouse_id:
            raise BusinessRuleViolationError("Cannot transfer to the same warehouse")

    @staticmethod
    def validate_document_status_transition(current_status: str, new_status: str, allowed_transitions: Dict[str, List[str]]) -> None:
        """Validate document status transition."""
        if current_status not in allowed_transitions:
            raise BusinessRuleViolationError(f"Invalid current status: {current_status}")

        if new_status not in allowed_transitions[current_status]:
            raise BusinessRuleViolationError(f"Cannot transition from {current_status} to {new_status}")

    @staticmethod
    def validate_inventory_operation(available_quantity: int, requested_quantity: int, operation: str) -> None:
        """Validate inventory operations."""
        if requested_quantity <= 0:
            raise BusinessRuleViolationError(f"Quantity for {operation} must be positive")

        if operation in ['remove', 'export'] and requested_quantity > available_quantity:
            raise BusinessRuleViolationError(f"Insufficient stock: requested {requested_quantity}, available {available_quantity}")


class DateUtils:
    """Utility class for date and time operations."""

    @staticmethod
    def get_current_datetime() -> datetime:
        """Get current datetime (could be mocked in tests)."""
        return datetime.now()

    @staticmethod
    def format_date_for_display(dt: datetime) -> str:
        """Format datetime for display purposes."""
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def is_date_in_range(target_date: date, start_date: date, end_date: date) -> bool:
        """Check if target date is within a date range."""
        return start_date <= target_date <= end_date


__all__ = [
    'ValidationUtils',
    'BusinessRulesUtils',
    'DateUtils'
]