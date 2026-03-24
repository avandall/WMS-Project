"""
Product domain logic for PMKT Warehouse Management System.
Contains business rules and validation for products.
"""

from typing import Optional
from app.exceptions.business_exceptions import (
    ValidationError,
    InvalidIDError,
    InvalidQuantityError,
)
from app.core.error_constants import ErrorMessages


class Product:
    """Domain class for Product with business logic and validation."""

    def __init__(
        self,
        product_id: int,
        name: str,
        description: Optional[str] = None,
        price: float = 0.0,
    ):
        self._validate_product_id(product_id)
        self._validate_name(name)
        self._validate_price(price)

        self.product_id = product_id
        self.name = name
        self.description = description
        self.price = price

    @staticmethod
    def _validate_product_id(product_id: int) -> None:
        """Validate product ID."""
        if not isinstance(product_id, int) or product_id <= 0:
            raise InvalidIDError(ErrorMessages.INVALID_PRODUCT_ID)

    @staticmethod
    def _validate_name(name: str) -> None:
        """Validate product name."""
        if not name or not isinstance(name, str) or len(name.strip()) == 0:
            raise ValidationError(ErrorMessages.INVALID_PRODUCT_NAME_EMPTY)
        if len(name) > 100:
            raise ValidationError(ErrorMessages.INVALID_PRODUCT_NAME_TOO_LONG)

    @staticmethod
    def _validate_price(price: float) -> None:
        """Validate product price."""
        if not isinstance(price, (int, float)) or price < 0:
            raise InvalidQuantityError(ErrorMessages.INVALID_PRODUCT_PRICE_NEGATIVE)

    def update_price(self, new_price: float) -> None:
        """Update product price with validation."""
        self._validate_price(new_price)
        self.price = new_price

    def update_name(self, new_name: str) -> None:
        """Update product name with validation."""
        self._validate_name(new_name)
        self.name = new_name

    def update_description(self, new_description: Optional[str]) -> None:
        """Update product description."""
        self.description = new_description

    def calculate_total_value(self, quantity: int) -> float:
        """Calculate total value for given quantity."""
        if quantity < 0:
            raise InvalidQuantityError(ErrorMessages.INVALID_QUANTITY_NEGATIVE)
        return self.price * quantity

    def __str__(self) -> str:
        return f"Product(id={self.product_id}, name='{self.name}', price={self.price})"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, Product):
            return False
        return self.product_id == other.product_id

    def __hash__(self) -> int:
        return hash(self.product_id)
