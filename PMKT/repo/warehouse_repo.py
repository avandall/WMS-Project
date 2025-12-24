from typing import Any, Dict
from ..domain.warehouse_domain import Warehouse
from ..domain.inventory_domain import InventoryItem
from ..module.custom_exceptions import InvalidQuantityError, WarehouseNotFoundError, InsufficientStockError, ProductNotFoundError

class WarehouseRepo:
    def __init__(self, inventory_repo=None):
        self.warehouses = {}
        self.inventory_repo = inventory_repo
    
    def create_warehouse(self, warehouse: Warehouse) -> None:
        self.warehouses[warehouse.warehouse_id] = warehouse
    
    def save(self, warehouse: Warehouse) -> None:
        self.warehouses[warehouse.warehouse_id] = warehouse
    
    def get(self, warehouse_id: int) -> Warehouse:
        return self.warehouses.get(warehouse_id)
   
    def delete(self, warehouse_id: int) -> None:
        if warehouse_id in self.warehouses:
            del self.warehouses[warehouse_id]

    def add_product_to_warehouse(self, warehouse_id: int, product_id: int, quantity: int) -> None:
        if quantity <= 0:
            raise InvalidQuantityError("Quantity must be positive")
        
        warehouse = self.get(warehouse_id)
        if not warehouse:
            raise WarehouseNotFoundError(f"Warehouse {warehouse_id} not found")
        
        # Update warehouse inventory
        for item in warehouse.inventory:
            if item.product_id == product_id:
                item.quantity += quantity
                break
        else:
            warehouse.inventory.append(InventoryItem(product_id=product_id, quantity=quantity))
        
        # Save warehouse
        self.save(warehouse)
        
        # Update total inventory
        if self.inventory_repo:
            self.inventory_repo.add_quantity(product_id, quantity)
    
    def remove_product_from_warehouse(self, warehouse_id: int, product_id: int, quantity: int) -> None:
        if quantity <= 0:
            raise InvalidQuantityError("Quantity must be positive")
        
        warehouse = self.get(warehouse_id)
        if not warehouse:
            raise WarehouseNotFoundError(f"Warehouse {warehouse_id} not found")
        
        # Update warehouse inventory
        for item in warehouse.inventory:
            if item.product_id == product_id:
                if item.quantity < quantity:
                    raise InsufficientStockError(f"Insufficient stock for product {product_id}")
                item.quantity -= quantity
                if item.quantity == 0:
                    warehouse.inventory.remove(item)
                break
        else:
            raise ProductNotFoundError(f"Product {product_id} not found in warehouse {warehouse_id}")
        
        # Save warehouse
        self.save(warehouse)
        
        # Update total inventory
        if self.inventory_repo:
            self.inventory_repo.remove_quantity(product_id, quantity)
    
    def get_warehouse_inventory(self, warehouse_id: int) -> list:
        warehouse = self.get(warehouse_id)
        return warehouse.inventory if warehouse else []