from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.business_exceptions import InvalidQuantityError
from app.models.inventory_domain import InventoryItem
from ..interfaces.interfaces import IInventoryRepo
from .models import InventoryModel


class InventoryRepo(IInventoryRepo):
    """PostgreSQL-backed repository for total inventory across all warehouses."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, inventory_item: InventoryItem) -> None:
        row = self.session.get(InventoryModel, inventory_item.product_id)
        if row:
            row.quantity = inventory_item.quantity
        else:
            row = InventoryModel(
                product_id=inventory_item.product_id, quantity=inventory_item.quantity
            )
            self.session.add(row)
        self.session.commit()

    def add_quantity(self, product_id: int, quantity: int) -> None:
        row = self.session.get(InventoryModel, product_id)
        
        if quantity < 0:
            if row:
                # Adding negative to existing product
                raise InvalidQuantityError("Cannot add negative quantity")
            else:
                # Starting with negative inventory
                raise InvalidQuantityError(
                    f"Cannot start with negative inventory for {product_id}"
                )

        if row:
            row.quantity += quantity
        else:
            row = InventoryModel(product_id=product_id, quantity=quantity)
            self.session.add(row)
        self.session.commit()

    def get_quantity(self, product_id: int) -> int:
        row = self.session.get(InventoryModel, product_id)
        return row.quantity if row else 0

    def get_all(self) -> List[InventoryItem]:
        rows = self.session.execute(select(InventoryModel)).scalars().all()
        return [self._to_domain(row) for row in rows]

    def delete(self, product_id: int) -> None:
        row = self.session.get(InventoryModel, product_id)
        if not row:
            raise KeyError("Product ID not found in inventory")
        if row.quantity != 0:
            raise InvalidQuantityError("Cannot delete item with non-zero quantity")
        self.session.delete(row)
        self.session.commit()

    def remove_quantity(self, product_id: int, quantity: int) -> None:
        row = self.session.get(InventoryModel, product_id)
        if not row:
            raise KeyError(f"Product {product_id} not found in inventory")
        if quantity < 0:
            raise InvalidQuantityError("Cannot remove negative quantity")
        if quantity > row.quantity:
            from app.exceptions.business_exceptions import InsufficientStockError
            raise InsufficientStockError(
                f"Insufficient stock. Available: {row.quantity}, Requested: {quantity}"
            )
        row.quantity -= quantity
        self.session.commit()

    @staticmethod
    def _to_domain(row: InventoryModel) -> InventoryItem:
        return InventoryItem(product_id=row.product_id, quantity=row.quantity)
