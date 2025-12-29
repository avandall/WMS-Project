from typing import Any, Dict, List
from app.models.warehouse_domain import Warehouse
from app.models.inventory_domain import InventoryItem
from app.exceptions.business_exceptions import InvalidQuantityError, WarehouseNotFoundError, InsufficientStockError, ProductNotFoundError
from ..interfaces.interfaces import IWarehouseRepo

class WarehouseRepo(IWarehouseRepo):
    def __init__(self):
        self.warehouses = {}
    
    def create_warehouse(self, warehouse: Warehouse) -> None:
        self.warehouses[warehouse.warehouse_id] = warehouse
    
    def save(self, warehouse: Warehouse) -> None:
        self.warehouses[warehouse.warehouse_id] = warehouse
    
    def get(self, warehouse_id: int) -> Warehouse:
        return self.warehouses.get(warehouse_id)
    
    def get_all(self) -> Dict[int, Warehouse]:
        return self.warehouses.copy()
   
    def delete(self, warehouse_id: int) -> None:
        if warehouse_id in self.warehouses:
            del self.warehouses[warehouse_id]

    def get_warehouse_inventory(self, warehouse_id: int) -> List[InventoryItem]:
        warehouse = self.get(warehouse_id)
        return warehouse.inventory if warehouse else []

    def add_product_to_warehouse(self, warehouse_id: int, product_id: int, quantity: int) -> None:
        warehouse = self.get(warehouse_id)
        if not warehouse:
            raise WarehouseNotFoundError(f"Warehouse {warehouse_id} not found")
        warehouse.add_product(product_id, quantity)
        self.save(warehouse)

    def remove_product_from_warehouse(self, warehouse_id: int, product_id: int, quantity: int) -> None:
        warehouse = self.get(warehouse_id)
        if not warehouse:
            raise WarehouseNotFoundError(f"Warehouse {warehouse_id} not found")
        warehouse.remove_product(product_id, quantity)
        self.save(warehouse)