from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.exceptions.business_exceptions import (
    InsufficientStockError,
    WarehouseNotFoundError,
)
from app.models.inventory_domain import InventoryItem
from app.models.warehouse_domain import Warehouse
from app.utils.infrastructure.id_generator import IDGenerator
from app.core.transaction import TransactionalRepository
from ..interfaces.interfaces import IWarehouseRepo
from .models import WarehouseInventoryModel, WarehouseModel


class WarehouseRepo(TransactionalRepository, IWarehouseRepo):
    """PostgreSQL-backed repository for warehouses and their inventory."""

    def __init__(self, session: Session):
        super().__init__(session)
        self._sync_id_generator()

    def _sync_id_generator(self) -> None:
        max_id = self.session.execute(
            select(func.max(WarehouseModel.warehouse_id))
        ).scalar()
        start_id = (max_id or 0) + 1
        IDGenerator.reset_generator("warehouse", start_id)

    def create_warehouse(self, warehouse: Warehouse) -> None:
        model = WarehouseModel(
            warehouse_id=warehouse.warehouse_id, location=warehouse.location
        )
        self.session.add(model)
        self._commit_if_auto()

    def save(self, warehouse: Warehouse) -> None:
        existing = self.session.get(WarehouseModel, warehouse.warehouse_id)
        if existing:
            existing.location = warehouse.location
        else:
            self.create_warehouse(warehouse)
            existing = self.session.get(WarehouseModel, warehouse.warehouse_id)

        # Save inventory items to warehouse_inventory table
        # Delete existing inventory entries directly - O(1) operation
        from sqlalchemy import delete

        self.session.execute(
            delete(WarehouseInventoryModel).where(
                WarehouseInventoryModel.warehouse_id == warehouse.warehouse_id
            )
        )

        # Add new inventory items
        for item in warehouse.inventory:
            inv_model = WarehouseInventoryModel(
                warehouse_id=warehouse.warehouse_id,
                product_id=item.product_id,
                quantity=item.quantity,
            )
            self.session.add(inv_model)

        self._commit_if_auto()

    def get(self, warehouse_id: int) -> Optional[Warehouse]:
        model = self.session.get(WarehouseModel, warehouse_id)
        if not model:
            return None
        return self._to_domain(model)

    def get_all(self) -> Dict[int, Warehouse]:
        from sqlalchemy.orm import joinedload

        # Eager load inventory_items to prevent N+1 queries - O(1) instead of O(n+1)
        rows = (
            self.session.execute(
                select(WarehouseModel).options(
                    joinedload(WarehouseModel.inventory_items)
                )
            )
            .unique()
            .scalars()
            .all()
        )
        return {row.warehouse_id: self._to_domain(row) for row in rows}

    def delete(self, warehouse_id: int) -> None:
        model = self.session.get(WarehouseModel, warehouse_id)
        if model:
            self.session.delete(model)
            self._commit_if_auto()

    def get_warehouse_inventory(self, warehouse_id: int) -> List[InventoryItem]:
        warehouse = self.session.get(WarehouseModel, warehouse_id)
        if not warehouse:
            return []
        inventory_rows = self.session.execute(
            select(WarehouseInventoryModel).where(
                WarehouseInventoryModel.warehouse_id == warehouse_id
            )
        ).scalars()
        return [InventoryItem(row.product_id, row.quantity) for row in inventory_rows]

    def add_product_to_warehouse(
        self, warehouse_id: int, product_id: int, quantity: int
    ) -> None:
        warehouse = self.session.get(WarehouseModel, warehouse_id)
        if not warehouse:
            raise WarehouseNotFoundError(f"Warehouse {warehouse_id} not found")

        row = self.session.execute(
            select(WarehouseInventoryModel).where(
                WarehouseInventoryModel.warehouse_id == warehouse_id,
                WarehouseInventoryModel.product_id == product_id,
            )
        ).scalar_one_or_none()

        if row:
            row.quantity += quantity
        else:
            row = WarehouseInventoryModel(
                warehouse_id=warehouse_id, product_id=product_id, quantity=quantity
            )
            self.session.add(row)

        self._commit_if_auto()

    def remove_product_from_warehouse(
        self, warehouse_id: int, product_id: int, quantity: int
    ) -> None:
        warehouse = self.session.get(WarehouseModel, warehouse_id)
        if not warehouse:
            raise WarehouseNotFoundError(f"Warehouse {warehouse_id} not found")

        row = self.session.execute(
            select(WarehouseInventoryModel).where(
                WarehouseInventoryModel.warehouse_id == warehouse_id,
                WarehouseInventoryModel.product_id == product_id,
            )
        ).scalar_one_or_none()

        if not row or row.quantity < quantity:
            raise InsufficientStockError(
                f"Warehouse {warehouse_id} does not have enough product {product_id}"
            )

        row.quantity -= quantity
        if row.quantity == 0:
            self.session.delete(row)

        self._commit_if_auto()

    def _to_domain(self, model: WarehouseModel) -> Warehouse:
        inventory = [
            InventoryItem(row.product_id, row.quantity) for row in model.inventory_items
        ]
        return Warehouse(
            warehouse_id=model.warehouse_id,
            location=model.location,
            inventory=inventory,
        )
