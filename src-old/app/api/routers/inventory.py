"""
Inventory API router.
Provides endpoints for inventory management operations.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.auth_deps import get_current_user, require_permissions
from app.core.permissions import Permission
from app.repositories.sql.models import WarehouseInventoryModel, WarehouseModel
from app.services.inventory_service import InventoryService

from ..dependencies import get_inventory_service, get_warehouse_repo
from ..schemas.product import InventoryItemResponse, WarehouseInventoryRowResponse

router = APIRouter(
    dependencies=[Depends(get_current_user), Depends(require_permissions(Permission.VIEW_INVENTORY))]
)


@router.get("/", response_model=List[InventoryItemResponse])
async def get_all_inventory(service: InventoryService = Depends(get_inventory_service)):
    """Get total inventory items (aggregated across warehouses)."""
    items = service.get_all_inventory_items()
    return [InventoryItemResponse.from_domain(item) for item in items]


@router.get("/by-warehouse", response_model=List[WarehouseInventoryRowResponse])
async def get_inventory_by_warehouse(
    warehouse_repo=Depends(get_warehouse_repo),
):
    """Get inventory rows per warehouse, including warehouse name."""

    session = warehouse_repo.session
    rows = session.execute(
        select(
            WarehouseInventoryModel.product_id,
            WarehouseInventoryModel.warehouse_id,
            WarehouseModel.location.label("warehouse_name"),
            WarehouseInventoryModel.quantity,
        ).join(
            WarehouseModel,
            WarehouseInventoryModel.warehouse_id == WarehouseModel.warehouse_id,
        )
    ).all()

    return [
        WarehouseInventoryRowResponse(
            product_id=row.product_id,
            warehouse_id=row.warehouse_id,
            warehouse_name=row.warehouse_name,
            quantity=row.quantity,
        )
        for row in rows
    ]


@router.get("/{product_id}")
async def get_product_quantity(
    product_id: int, service: InventoryService = Depends(get_inventory_service)
):
    """Get total quantity for a specific product."""
    quantity = service.get_total_quantity(product_id)
    return {"product_id": product_id, "quantity": quantity}
