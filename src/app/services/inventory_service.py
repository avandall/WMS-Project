from typing import List, Dict, Any
from app.repositories.interfaces.interfaces import (
    IInventoryRepo,
    IProductRepo,
    IWarehouseRepo,
)
from app.exceptions.business_exceptions import (
    InvalidQuantityError,
    EntityNotFoundError,
    InsufficientStockError,
)
from app.models.inventory_domain import InventoryItem
from app.core.logging import get_logger

logger = get_logger(__name__)


class InventoryService:
    """
    Service layer for inventory management orchestration.
    Coordinates inventory operations across the system and provides business-level inventory insights.
    """

    def __init__(
        self,
        inventory_repo: IInventoryRepo,
        product_repo: IProductRepo,
        warehouse_repo: IWarehouseRepo,
    ):
        self.inventory_repo = inventory_repo
        self.product_repo = product_repo
        self.warehouse_repo = warehouse_repo

    def add_to_total_inventory(self, product_id: int, quantity: int) -> None:
        """
        Add quantity to total inventory with business orchestration.
        - Validates product exists
        - Validates quantity
        - Updates total inventory
        """
        if quantity < 0:
            raise InvalidQuantityError("Cannot add negative quantity to inventory")

        # Validate product exists
        product = self.product_repo.get(product_id)
        if not product:
            raise EntityNotFoundError(f"Product {product_id} not found")

        self.inventory_repo.add_quantity(product_id, quantity)

    def remove_from_total_inventory(self, product_id: int, quantity: int) -> None:
        """
        Remove quantity from total inventory with business orchestration.
        - Validates product exists
        - Validates sufficient inventory
        - Updates total inventory
        """
        if quantity < 0:
            raise InvalidQuantityError("Cannot remove negative quantity from inventory")

        # Validate product exists
        product = self.product_repo.get(product_id)
        if not product:
            raise EntityNotFoundError(f"Product {product_id} not found")

        # Check sufficient inventory
        current_quantity = self.inventory_repo.get_quantity(product_id)
        if current_quantity < quantity:
            raise InsufficientStockError(
                f"Insufficient inventory: only {current_quantity} items available"
            )

        self.inventory_repo.remove_quantity(product_id, quantity)

    def get_total_quantity(self, product_id: int) -> int:
        """
        Get total quantity with validation.
        """
        # Validate product exists
        product = self.product_repo.get(product_id)
        if not product:
            raise EntityNotFoundError(f"Product {product_id} not found")

        return self.inventory_repo.get_quantity(product_id)

    def get_inventory_status(self, product_id: int) -> Dict[str, Any]:
        """
        Get comprehensive inventory status for a product.
        Orchestrates between inventory, product, and warehouse repositories.
        """
        # Validate product exists
        product = self.product_repo.get(product_id)
        if not product:
            raise EntityNotFoundError(f"Product {product_id} not found")

        total_quantity = self.inventory_repo.get_quantity(product_id)

        # Get warehouse distribution
        warehouse_distribution = []
        total_warehouses = 0
        total_allocated = 0

        for warehouse_id, warehouse in self.warehouse_repo.get_all().items():
            inventory = self.warehouse_repo.get_warehouse_inventory(warehouse_id)
            for item in inventory:
                if item.product_id == product_id:
                    warehouse_distribution.append(
                        {
                            "warehouse_id": warehouse_id,
                            "warehouse_location": warehouse.location,
                            "quantity": item.quantity,
                        }
                    )
                    total_warehouses += 1
                    total_allocated += item.quantity
                    break

        unallocated_quantity = total_quantity - total_allocated

        return {
            "product": product,
            "total_quantity": total_quantity,
            "allocated_quantity": total_allocated,
            "unallocated_quantity": unallocated_quantity,
            "warehouse_count": total_warehouses,
            "warehouse_distribution": warehouse_distribution,
        }

    def get_all_inventory_with_details(self) -> List[Dict[str, Any]]:
        """
        Get all inventory items with product details.
        """
        all_inventory = self.inventory_repo.get_all()
        result = []

        for item in all_inventory:
            try:
                product = self.product_repo.get(item.product_id)
                if product:  # Product might have been deleted
                    status = self.get_inventory_status(item.product_id)
                    result.append(status)
            except EntityNotFoundError:
                # Product was deleted but inventory remains
                continue

        return result

    def get_low_stock_products(self, threshold: int = 10) -> List[Dict[str, Any]]:
        """
        Get products with low inventory levels.
        Business logic for identifying products that need restocking.
        """
        if threshold < 0:
            raise InvalidQuantityError("Threshold must be non-negative")

        low_stock_products = []
        all_inventory = self.inventory_repo.get_all()

        for item in all_inventory:
            try:
                product = self.product_repo.get(item.product_id)
                if product and item.quantity <= threshold:
                    low_stock_products.append(
                        {
                            "product": product,
                            "current_quantity": item.quantity,
                            "threshold": threshold,
                            "needs_restock": True,
                        }
                    )
            except EntityNotFoundError:
                continue

        return low_stock_products

    def get_all_inventory_items(self) -> List[InventoryItem]:
        """Return raw inventory items for simple listings."""
        return self.inventory_repo.get_all()

    def get_inventory_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive inventory summary across the entire system.
        """
        all_inventory = self.inventory_repo.get_all()
        total_products = len(all_inventory)
        total_items = sum(item.quantity for item in all_inventory)

        # Get warehouse distribution summary
        warehouse_summary = {}
        for warehouse_id, warehouse in self.warehouse_repo.get_all().items():
            inventory = self.warehouse_repo.get_warehouse_inventory(warehouse_id)
            warehouse_items = sum(item.quantity for item in inventory)
            warehouse_products = len(inventory)

            warehouse_summary[warehouse_id] = {
                "location": warehouse.location,
                "total_items": warehouse_items,
                "unique_products": warehouse_products,
            }

        return {
            "total_products": total_products,
            "total_inventory_items": total_items,
            "warehouse_count": len(warehouse_summary),
            "warehouse_summary": warehouse_summary,
            "low_stock_products": self.get_low_stock_products(),
        }

    def validate_inventory_consistency(self) -> List[str]:
        """
        Validate inventory consistency across the system.
        Checks for discrepancies between total inventory and warehouse allocations.
        """
        issues = []
        all_inventory = self.inventory_repo.get_all()

        for item in all_inventory:
            try:
                product = self.product_repo.get(item.product_id)
                if not product:
                    issues.append(
                        f"Orphaned inventory: product {item.product_id} not found"
                    )
                    continue

                # Check consistency with warehouse allocations
                total_allocated = 0
                for warehouse_id in self.warehouse_repo.get_all().keys():
                    inventory = self.warehouse_repo.get_warehouse_inventory(
                        warehouse_id
                    )
                    for wh_item in inventory:
                        if wh_item.product_id == item.product_id:
                            total_allocated += wh_item.quantity
                            break

                if total_allocated > item.quantity:
                    issues.append(
                        f"Inconsistency for product {item.product_id}: "
                        f"allocated {total_allocated} > total {item.quantity}"
                    )

            except EntityNotFoundError:
                issues.append(
                    f"Product {item.product_id} not found for inventory validation"
                )

        return issues
