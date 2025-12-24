"""
Custom exceptions for the PMKT Warehouse Management System.
Comprehensive exception hierarchy following Clean Architecture principles.
"""

from typing import Any, Optional


# Base Exception Classes
class PMKTException(Exception):
    """Base exception for all PMKT-related errors."""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class PMKTError(PMKTException):
    """General PMKT error for unexpected conditions."""
    pass


# Domain Layer Exceptions
class DomainException(PMKTException):
    """Base class for domain layer exceptions."""
    pass


class ValidationError(DomainException):
    """Raised when domain validation fails."""
    pass


class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated."""
    pass


class EntityNotFoundError(DomainException):
    """Raised when a domain entity is not found."""
    pass


class EntityAlreadyExistsError(DomainException):
    """Raised when trying to create an entity that already exists."""
    pass


# Application Layer Exceptions
class ApplicationException(PMKTException):
    """Base class for application layer exceptions."""
    pass


class ApplicationError(ApplicationException):
    """General application error."""
    pass


class UseCaseError(ApplicationException):
    """Raised when a use case cannot be executed."""
    pass


class InvalidOperationError(ApplicationException):
    """Raised when an operation is invalid in the current context."""
    pass


# Infrastructure Layer Exceptions
class InfrastructureException(PMKTException):
    """Base class for infrastructure layer exceptions."""
    pass


class RepositoryError(InfrastructureException):
    """Raised when repository operations fail."""
    pass


class DataAccessError(InfrastructureException):
    """Raised when data access operations fail."""
    pass


class ExternalServiceError(InfrastructureException):
    """Raised when external service calls fail."""
    pass


# Specific Business Exceptions
class InsufficientStockError(BusinessRuleViolationError):
    """Raised when there is not enough stock to fulfill a request."""
    pass


class WarehouseNotFoundError(EntityNotFoundError):
    """Raised when a requested warehouse does not exist."""
    pass


class ProductNotFoundError(EntityNotFoundError):
    """Raised when a requested product is not found."""
    pass


class DocumentNotFoundError(EntityNotFoundError):
    """Raised when a requested document does not exist."""
    pass


class InvalidDocumentStatusError(BusinessRuleViolationError):
    """Raised when trying to perform an operation on a document with invalid status."""
    pass


class InvalidQuantityError(ValidationError):
    """Raised when an invalid quantity is provided (e.g., negative)."""
    pass


class InvalidIDError(ValidationError):
    """Raised when an invalid ID is provided (e.g., non-positive integer)."""
    pass


class DuplicateWarehouseError(EntityAlreadyExistsError):
    """Raised when trying to create a warehouse with an existing ID."""
    pass


class DuplicateProductError(EntityAlreadyExistsError):
    """Raised when trying to create a product with an existing ID."""
    pass


class DuplicateDocumentError(EntityAlreadyExistsError):
    """Raised when trying to create a document with an existing ID."""
    pass


# Report and Analytics Exceptions
class ReportGenerationError(ApplicationError):
    """Raised when there is an error generating a report."""
    pass


class InvalidReportParametersError(ValidationError):
    """Raised when invalid parameters are provided for report generation."""
    pass


class AnalyticsError(ApplicationError):
    """Raised when analytics operations fail."""
    pass


# API and Interface Exceptions
class APIException(PMKTException):
    """Base class for API-related exceptions."""
    pass


class AuthenticationError(APIException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(APIException):
    """Raised when authorization fails."""
    pass


class RateLimitError(APIException):
    """Raised when rate limit is exceeded."""
    pass


class InputValidationError(APIException):
    """Raised when API input validation fails."""
    pass


# Configuration and Setup Exceptions
class ConfigurationError(PMKTException):
    """Raised when there are configuration issues."""
    pass


class InitializationError(PMKTException):
    """Raised when system initialization fails."""
    pass


# Legacy compatibility (keep for backward compatibility)
# These will be deprecated in future versions
class WarehouseNotFoundException(WarehouseNotFoundError):
    """Deprecated: Use WarehouseNotFoundError instead."""
    pass


class ProductNotFoundException(ProductNotFoundError):
    """Deprecated: Use ProductNotFoundError instead."""
    pass


# Exception Factory Functions
def create_validation_error(field: str, value: Any, constraint: str) -> ValidationError:
    """Factory function for creating validation errors."""
    return ValidationError(
        f"Validation failed for field '{field}' with value '{value}': {constraint}",
        details={"field": field, "value": value, "constraint": constraint}
    )


def create_business_rule_error(rule: str, context: Optional[dict] = None) -> BusinessRuleViolationError:
    """Factory function for creating business rule violation errors."""
    return BusinessRuleViolationError(
        f"Business rule violated: {rule}",
        details=context or {}
    )


def create_entity_not_found_error(entity_type: str, entity_id: Any) -> EntityNotFoundError:
    """Factory function for creating entity not found errors."""
    return EntityNotFoundError(
        f"{entity_type} with ID '{entity_id}' not found",
        details={"entity_type": entity_type, "entity_id": entity_id}
    )


# Exception Hierarchy Summary
__all__ = [
    # Base classes
    'PMKTException',
    'PMKTError',

    # Domain layer
    'DomainException',
    'ValidationError',
    'BusinessRuleViolationError',
    'EntityNotFoundError',
    'EntityAlreadyExistsError',

    # Application layer
    'ApplicationException',
    'ApplicationError',
    'UseCaseError',
    'InvalidOperationError',

    # Infrastructure layer
    'InfrastructureException',
    'RepositoryError',
    'DataAccessError',
    'ExternalServiceError',

    # Specific business exceptions
    'InsufficientStockError',
    'WarehouseNotFoundError',
    'ProductNotFoundError',
    'DocumentNotFoundError',
    'InvalidDocumentStatusError',
    'InvalidQuantityError',
    'InvalidIDError',
    'DuplicateWarehouseError',
    'DuplicateProductError',
    'DuplicateDocumentError',

    # Report and analytics
    'ReportGenerationError',
    'InvalidReportParametersError',
    'AnalyticsError',

    # API and interface
    'APIException',
    'AuthenticationError',
    'AuthorizationError',
    'RateLimitError',
    'InputValidationError',

    # Configuration
    'ConfigurationError',
    'InitializationError',

    # Legacy (deprecated)
    'WarehouseNotFoundException',
    'ProductNotFoundException',

    # Factory functions
    'create_validation_error',
    'create_business_rule_error',
    'create_entity_not_found_error'
]