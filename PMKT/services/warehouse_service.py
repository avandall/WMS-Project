from ..domain.warehouse_domain import Warehouse
from ..domain.inventory_domain import InventoryItem
from ..module.custom_exceptions import InvalidQuantityError, WarehouseNotFoundError, InsufficientStockError, ProductNotFoundError
from ..repo.warehouse_repo import WarehouseRepo
from ..utils.infrastructure import warehouse_id_generator

class WarehouseService:
    def __init__(self, repo: WarehouseRepo):
        self.repo = repo
        self._warehouse_id_generator = warehouse_id_generator()

    def add_product_to_warehouse(self, warehouse_id: int, product_id: int, quantity: int) -> None:
        self.repo.add_product_to_warehouse(warehouse_id, product_id, quantity)
    
    def remove_product_from_warehouse(self, warehouse_id: int, product_id: int, quantity: int) -> None:
        self.repo.remove_product_from_warehouse(warehouse_id, product_id, quantity)
    
    def get_warehouse_inventory(self, warehouse_id: int) -> list:
        return self.repo.get_warehouse_inventory(warehouse_id)
    
    def get_warehouse(self, warehouse_id: int) -> Warehouse:
        """Get warehouse by ID."""
        warehouse = self.repo.get(warehouse_id)
        if not warehouse:
            raise WarehouseNotFoundError(f"Warehouse {warehouse_id} not found")
        return warehouse
    
    def create_warehouse(self, location: str) -> Warehouse:
        """Create a new warehouse with auto-generated ID."""
        warehouse_id = self._warehouse_id_generator()
        warehouse = Warehouse(warehouse_id=warehouse_id, location=location)
        self.repo.create_warehouse(warehouse)
        return warehouse

    def create_warehouse_with_id(self, warehouse: Warehouse) -> None:
        """Create a warehouse with pre-defined ID."""
        self.repo.create_warehouse(warehouse)

    