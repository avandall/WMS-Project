"""
Warehouse domain logic for PMKT Warehouse Management System.
Contains business rules and validation for warehouse operations.
"""

from typing import Optional, List
from ..module.custom_exceptions import ValidationError, BusinessRuleViolationError, EntityAlreadyExistsError
from ..module.custom_exceptions import InvalidIDError, InvalidQuantityError, WarehouseNotFoundError, ProductNotFoundError, InsufficientStockError
from ..module.error_constants import ErrorMessages
from .inventory_domain import InventoryItem

class Warehouse:
    """Domain class for Warehouse with business logic and validation."""

    def __init__(self, warehouse_id: int, location: str, inventory: Optional[List[InventoryItem]] = None):
        self._validate_warehouse_id(warehouse_id)
        self._validate_location(location)

        self.warehouse_id = warehouse_id
        self.location = location
        self.inventory: List[InventoryItem] = inventory or []

    @staticmethod
    def _validate_warehouse_id(warehouse_id: int) -> None:
        """Validate warehouse ID."""
        if not isinstance(warehouse_id, int) or warehouse_id <= 0:
            raise InvalidIDError(ErrorMessages.INVALID_WAREHOUSE_ID)

    @staticmethod
    def _validate_location(location: str) -> None:
        """Validate warehouse location."""
        if not location or not isinstance(location, str) or len(location.strip()) == 0:
            raise ValidationError(ErrorMessages.INVALID_WAREHOUSE_LOCATION_EMPTY)
        if len(location) > 200:
            raise ValidationError(ErrorMessages.INVALID_WAREHOUSE_LOCATION_TOO_LONG)

    def add_product(self, product_id: str, quantity: int) -> None:
        """Add product to warehouse inventory."""
        if quantity <= 0:
            raise InvalidQuantityError(ErrorMessages.INVALID_QUANTITY_POSITIVE)

        # Find existing item or create new one
        for item in self.inventory:
            if item.product_id == product_id:
                item.add_quantity(quantity)
                return

        # Create new inventory item
        new_item = InventoryItem(product_id, quantity)
        self.inventory.append(new_item)

    def remove_product(self, product_id: str, quantity: int) -> None:
        """Remove product from warehouse inventory."""
        if quantity <= 0:
            raise InvalidQuantityError(ErrorMessages.INVALID_QUANTITY_POSITIVE)

        for i, item in enumerate(self.inventory):
            if item.product_id == product_id:
                if item.quantity < quantity:
                    raise InsufficientStockError(
                        ErrorMessages.INSUFFICIENT_STOCK.format(
                            available=item.quantity,
                            requested=quantity
                        )
                    )
                item.remove_quantity(quantity)
                # Remove item if quantity becomes zero
                if item.is_empty():
                    self.inventory.pop(i)
                return

        raise ProductNotFoundError(
            ErrorMessages.PRODUCT_NOT_FOUND_IN_WAREHOUSE.format(
                product_id=product_id,
                warehouse_id=self.warehouse_id
            )
        )

    def get_product_quantity(self, product_id: str) -> int:
        """Get quantity of a product in this warehouse."""
        for item in self.inventory:
            if item.product_id == product_id:
                return item.quantity
        return 0

    def has_product(self, product_id: str) -> bool:
        """Check if warehouse has a specific product."""
        return any(item.product_id == product_id for item in self.inventory)

    def get_inventory_value(self, products: dict) -> float:
        """Calculate total inventory value for this warehouse."""
        total_value = 0.0
        for item in self.inventory:
            if item.product_id in products:
                product = products[item.product_id]
                total_value += product.calculate_total_value(item.quantity)
        return total_value

    def get_inventory_summary(self) -> dict:
        """Get summary of warehouse inventory."""
        return {
            'warehouse_id': self.warehouse_id,
            'location': self.location,
            'total_products': len(self.inventory),
            'total_items': sum(item.quantity for item in self.inventory)
        }

    def transfer_product_to(self, other_warehouse: 'Warehouse', product_id: str, quantity: int) -> None:
        """Transfer product to another warehouse."""
        if other_warehouse.warehouse_id == self.warehouse_id:
            raise BusinessRuleViolationError(ErrorMessages.CANNOT_TRANSFER_SAME_WAREHOUSE)

        # Remove from this warehouse
        self.remove_product(product_id, quantity)
        # Add to other warehouse
        other_warehouse.add_product(product_id, quantity)

    def update_location(self, new_location: str) -> None:
        """Update warehouse location."""
        self._validate_location(new_location)
        self.location = new_location

    def __str__(self) -> str:
        return f"Warehouse(id={self.warehouse_id}, location='{self.location}', products={len(self.inventory)})"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, Warehouse):
            return False
        return self.warehouse_id == other.warehouse_id

    def __hash__(self) -> int:
        return hash(self.warehouse_id)


class WarehouseManager:
    """Manager class for handling multiple warehouses."""

    def __init__(self):
        self._warehouses: dict[int, Warehouse] = {}

    def add_warehouse(self, warehouse: Warehouse) -> None:
        """Add a warehouse."""
        if warehouse.warehouse_id in self._warehouses:
            raise EntityAlreadyExistsError(f"Warehouse {warehouse.warehouse_id} already exists")
        self._warehouses[warehouse.warehouse_id] = warehouse

    def get_warehouse(self, warehouse_id: int) -> Warehouse:
        """Get warehouse by ID."""
        if warehouse_id not in self._warehouses:
            raise WarehouseNotFoundError(f"Warehouse {warehouse_id} not found")
        return self._warehouses[warehouse_id]

    def remove_warehouse(self, warehouse_id: int) -> None:
        """Remove a warehouse."""
        if warehouse_id not in self._warehouses:
            raise WarehouseNotFoundError(f"Warehouse {warehouse_id} not found")
        del self._warehouses[warehouse_id]

    def get_all_warehouses(self) -> List[Warehouse]:
        """Get all warehouses."""
        return list(self._warehouses.values())

    def find_warehouses_with_product(self, product_id: str) -> List[Warehouse]:
        """Find warehouses that contain a specific product."""
        return [w for w in self._warehouses.values() if w.has_product(product_id)]

    def get_total_product_quantity(self, product_id: str) -> int:
        """Get total quantity of a product across all warehouses."""
        return sum(w.get_product_quantity(product_id) for w in self._warehouses.values())

    def __len__(self) -> int:
        return len(self._warehouses)

    def __str__(self) -> str:
        return f"WarehouseManager(warehouses={len(self._warehouses)})"