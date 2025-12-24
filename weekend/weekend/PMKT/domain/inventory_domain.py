"""
Inventory domain logic for PMKT Warehouse Management System.
Contains business rules and validation for inventory management.
"""

from ..module.custom_exceptions import ValidationError
from ..module.custom_exceptions import InvalidQuantityError, InsufficientStockError
from .product_domain import Product

class InventoryItem:
    """Domain class for InventoryItem with business logic and validation."""

    def __init__(self, product_id: int, quantity: int = 0):
        self._validate_product_id(product_id)
        self._validate_quantity(quantity)

        self.product_id = product_id
        self.quantity = quantity

    @staticmethod
    def _validate_product_id(product_id: int) -> None:
        """Validate product ID."""
        if not isinstance(product_id, int) or product_id <= 0:
            raise ValidationError("Product ID must be a positive integer")

    @staticmethod
    def _validate_quantity(quantity: int) -> None:
        """Validate quantity."""
        if not isinstance(quantity, int) or quantity < 0:
            raise InvalidQuantityError("Quantity must be a non-negative integer")

    def add_quantity(self, amount: int) -> None:
        """Add quantity to inventory."""
        if amount < 0:
            raise InvalidQuantityError("Cannot add negative quantity")
        new_quantity = self.quantity + amount
        self._validate_quantity(new_quantity)
        self.quantity = new_quantity

    def remove_quantity(self, amount: int) -> None:
        """Remove quantity from inventory."""
        if amount < 0:
            raise InvalidQuantityError("Cannot remove negative quantity")
        if amount > self.quantity:
            raise InsufficientStockError(f"Insufficient stock. Available: {self.quantity}, Requested: {amount}")
        self.quantity -= amount

    def has_sufficient_stock(self, requested_quantity: int) -> bool:
        """Check if there's sufficient stock for the requested quantity."""
        return self.quantity >= requested_quantity

    def is_empty(self) -> bool:
        """Check if inventory item is empty."""
        return self.quantity == 0

    def __str__(self) -> str:
        return f"InventoryItem(product_id='{self.product_id}', quantity={self.quantity})"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, InventoryItem):
            return False
        return self.product_id == other.product_id

    def __hash__(self) -> int:
        return hash(self.product_id)