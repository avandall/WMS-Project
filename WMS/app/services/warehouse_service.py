from typing import List, Dict, Any
from app.models.warehouse_domain import Warehouse
from app.models.inventory_domain import InventoryItem
from app.exceptions.business_exceptions import (
    InvalidQuantityError,
    WarehouseNotFoundError,
    InsufficientStockError,
    ProductNotFoundError,
    ValidationError,
    EntityAlreadyExistsError,
)
from app.repositories.interfaces.interfaces import (
    IWarehouseRepo,
    IProductRepo,
    IInventoryRepo,
)
from app.utils.infrastructure import warehouse_id_generator
from app.core.logging import get_logger

logger = get_logger(__name__)


class WarehouseService:
    """
    Service layer for warehouse management orchestration.
    Coordinates between warehouse, product, and inventory repositories.
    """

    def __init__(
        self,
        warehouse_repo: IWarehouseRepo,
        product_repo: IProductRepo,
        inventory_repo: IInventoryRepo,
        id_generator=None,
    ):
        self.warehouse_repo = warehouse_repo
        self.product_repo = product_repo
        self.inventory_repo = inventory_repo
        self._warehouse_id_generator = id_generator or warehouse_id_generator()

    def create_warehouse(self, location: str) -> Warehouse:
        """
        Create a new warehouse with business orchestration.
        - Validates location uniqueness
        - Generates unique ID
        - Initializes warehouse
        """
        # Business rule: Check for duplicate locations (optional)
        # This could be implemented based on business requirements

        warehouse_id = self._warehouse_id_generator()
        warehouse = Warehouse(warehouse_id=warehouse_id, location=location)
        self.warehouse_repo.create_warehouse(warehouse)
        return warehouse

    def create_warehouse_with_id(self, warehouse: Warehouse) -> None:
        """
        Create a warehouse with pre-defined ID (for imports/migrations).
        """
        existing = self.warehouse_repo.get(warehouse.warehouse_id)
        if existing:
            raise EntityAlreadyExistsError(
                f"Warehouse with ID {warehouse.warehouse_id} already exists"
            )

        self.warehouse_repo.create_warehouse(warehouse)

    def get_warehouse(self, warehouse_id: int) -> Warehouse:
        """
        Get warehouse with validation.
        """
        warehouse = self.warehouse_repo.get(warehouse_id)
        if not warehouse:
            raise WarehouseNotFoundError(f"Warehouse {warehouse_id} not found")
        return warehouse

    def add_product_to_warehouse(
        self, warehouse_id: int, product_id: int, quantity: int
    ) -> None:
        """
        Add product to warehouse with business orchestration.
        - Validates warehouse exists
        - Validates product exists
        - Validates quantity
        - Checks total inventory availability
        - Updates warehouse inventory
        """
        # Validate inputs
        if quantity <= 0:
            raise InvalidQuantityError("Quantity must be positive")

        # Validate warehouse exists
        self.get_warehouse(warehouse_id)

        # Validate product exists
        product = self.product_repo.get(product_id)
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")

        # Add to warehouse (repository handles the actual storage)
        self.warehouse_repo.add_product_to_warehouse(warehouse_id, product_id, quantity)

    def remove_product_from_warehouse(
        self, warehouse_id: int, product_id: int, quantity: int
    ) -> None:
        """
        Remove product from warehouse with business orchestration.
        - Validates warehouse and product exist
        - Validates sufficient quantity in warehouse
        - Updates warehouse inventory
        """
        # Validate inputs
        if quantity <= 0:
            raise InvalidQuantityError("Quantity must be positive")

        # Validate warehouse exists
        self.get_warehouse(warehouse_id)

        # Validate product exists
        product = self.product_repo.get(product_id)
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")

        # Check current warehouse quantity
        current_quantity = self._get_warehouse_product_quantity(
            warehouse_id, product_id
        )
        if current_quantity < quantity:
            raise InsufficientStockError(
                f"Insufficient stock in warehouse: only {current_quantity} items available"
            )

        # Remove from warehouse
        self.warehouse_repo.remove_product_from_warehouse(
            warehouse_id, product_id, quantity
        )

    def get_warehouse_inventory(self, warehouse_id: int) -> List[InventoryItem]:
        """
        Get warehouse inventory items.
        Returns raw inventory items for API responses.
        """
        # Validate warehouse exists
        self.get_warehouse(warehouse_id)

        # Get raw inventory
        inventory_items = self.warehouse_repo.get_warehouse_inventory(warehouse_id)

        return inventory_items

    def transfer_product(
        self,
        from_warehouse_id: int,
        to_warehouse_id: int,
        product_id: int,
        quantity: int,
    ) -> None:
        """
        Transfer product between warehouses with business orchestration.
        - Validates both warehouses exist
        - Validates product exists
        - Ensures sufficient quantity in source warehouse
        - Performs the transfer as atomic operation
        """
        if quantity <= 0:
            raise InvalidQuantityError("Transfer quantity must be positive")

        if from_warehouse_id == to_warehouse_id:
            raise ValidationError("Cannot transfer to the same warehouse")

        # Validate both warehouses exist
        self.get_warehouse(from_warehouse_id)
        self.get_warehouse(to_warehouse_id)

        # Validate product exists
        product = self.product_repo.get(product_id)
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")

        # Check source warehouse has enough
        source_quantity = self._get_warehouse_product_quantity(
            from_warehouse_id, product_id
        )
        if source_quantity < quantity:
            raise InsufficientStockError(
                f"Source warehouse only has {source_quantity} items"
            )

        # Perform transfer (remove from source, add to destination)
        self.warehouse_repo.remove_product_from_warehouse(
            from_warehouse_id, product_id, quantity
        )
        self.warehouse_repo.add_product_to_warehouse(
            to_warehouse_id, product_id, quantity
        )

    def get_all_warehouses_with_inventory_summary(self) -> List[Dict[str, Any]]:
        """
        Get all warehouses with inventory summaries.
        Orchestrates comprehensive warehouse and inventory data.
        """
        warehouses = self.warehouse_repo.get_all()
        result = []

        for warehouse in warehouses.values():
            inventory = self.get_warehouse_inventory(warehouse.warehouse_id)
            total_items = sum(item.quantity for item in inventory)
            unique_products = len(inventory)

            result.append(
                {
                    "warehouse": warehouse,
                    "inventory_summary": {
                        "total_items": total_items,
                        "unique_products": unique_products,
                        "inventory_details": inventory,
                    },
                }
            )

        return result

    def _get_warehouse_product_quantity(
        self, warehouse_id: int, product_id: int
    ) -> int:
        """
        Helper method to get quantity of specific product in warehouse.
        """
        inventory = self.warehouse_repo.get_warehouse_inventory(warehouse_id)
        for item in inventory:
            if item.product_id == product_id:
                return item.quantity
        return 0

    def transfer_all_inventory(
        self, from_warehouse_id: int, to_warehouse_id: int
    ) -> List[InventoryItem]:
        """
        Transfer all inventory from one warehouse to another.
        Used before deleting a warehouse to preserve inventory.

        Returns list of transferred items.
        """
        if from_warehouse_id == to_warehouse_id:
            raise ValidationError("Cannot transfer to the same warehouse")

        # Validate both warehouses exist
        self.get_warehouse(from_warehouse_id)
        self.get_warehouse(to_warehouse_id)

        # Get all inventory from source warehouse
        source_inventory = self.warehouse_repo.get_warehouse_inventory(
            from_warehouse_id
        )

        if not source_inventory:
            return []

        # Transfer each product
        transferred_items = []
        for item in source_inventory:
            # Transfer using existing transfer logic
            self.warehouse_repo.remove_product_from_warehouse(
                from_warehouse_id, item.product_id, item.quantity
            )
            self.warehouse_repo.add_product_to_warehouse(
                to_warehouse_id, item.product_id, item.quantity
            )
            transferred_items.append(item)

        return transferred_items

    def delete_warehouse(self, warehouse_id: int) -> None:
        """
        Delete a warehouse with business validation.
        - Validates warehouse exists
        - Ensures warehouse has no inventory (stock = 0)
        - Deletes the warehouse
        """
        # Validate warehouse exists
        self.get_warehouse(warehouse_id)

        # Check if warehouse has any inventory
        inventory = self.warehouse_repo.get_warehouse_inventory(warehouse_id)
        if inventory:
            total_items = sum(item.quantity for item in inventory)
            unique_products = len(inventory)
            raise ValidationError(
                f"Cannot delete warehouse {warehouse_id}: warehouse still has {total_items} items "
                f"({unique_products} unique products) in stock. "
                f"Use the transfer endpoint to move inventory to another warehouse first."
            )

        # Delete warehouse
        self.warehouse_repo.delete(warehouse_id)
