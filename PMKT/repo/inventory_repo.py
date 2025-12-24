from ..domain.inventory_domain import InventoryItem
from ..module.custom_exceptions import InvalidQuantityError
from typing import Dict, List
# Repository for total inventory of all warehouses

class InventoryRepo:
    def __init__(self):
        self.inventory: Dict[int, InventoryItem] = {}

    def save(self, inventory_item: InventoryItem) -> None:
        self.inventory[inventory_item.product_id] = inventory_item

    def add_quantity(self, product_id: int, quantity: int) -> None:
        if product_id in self.inventory:
            self.inventory[product_id].add_quantity(quantity)
        else:
            if quantity < 0:
                raise InvalidQuantityError(f"Cannot start with negative inventory for {product_id}")
            item = InventoryItem(product_id, quantity)
            self.inventory[product_id] = item

    def get_quantity(self, product_id: int) -> int:
        item = self.inventory.get(product_id)
        return item.quantity if item else 0

    def get_all(self) -> List[InventoryItem]:
        return list(self.inventory.values())

    def delete(self, product_id: int) -> None:
        if product_id in self.inventory:
            item = self.inventory[product_id]
            if not item.is_empty():
                raise InvalidQuantityError("Cannot delete item with non-zero quantity")
            del self.inventory[product_id]
        else:
            raise KeyError("Product ID not found in inventory")
    
    def remove_quantity(self, product_id: int, quantity: int) -> None:
        if product_id not in self.inventory:
            raise KeyError(f"Product {product_id} not found in inventory")
        self.inventory[product_id].remove_quantity(quantity)