from ..repo.inventory_repo import InventoryRepo

# Service class for managing inventory items
class InventoryService:
    def __init__(self, repo: InventoryRepo):
        self.repo = repo
    
    def add_to_total(self, product_id: int, quantity: int) -> None:
        self.repo.add_quantity(product_id, quantity)
    
    def get_total_quantity(self, product_id: int) -> int:
        return self.repo.get_quantity(product_id)
    
    def get_all_inventory(self) -> list:
        return self.repo.get_all()
    
    