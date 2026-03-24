"""
Inventory API router.
Provides endpoints for inventory management operations.
"""

from typing import List
from fastapi import APIRouter, Depends
from ..dependencies import get_inventory_service
from ..schemas.product import InventoryItemResponse
from app.api.auth_deps import get_current_user, require_permissions
from app.core.permissions import Permission
from app.services.inventory_service import InventoryService

router = APIRouter(dependencies=[Depends(get_current_user), Depends(require_permissions(Permission.VIEW_INVENTORY))])


@router.get("/", response_model=List[InventoryItemResponse])
async def get_all_inventory(service: InventoryService = Depends(get_inventory_service)):
    """Get all inventory items."""
    items = service.get_all_inventory_items()
    return [InventoryItemResponse.from_domain(item) for item in items]


@router.get("/{product_id}")
async def get_product_quantity(
    product_id: int, service: InventoryService = Depends(get_inventory_service)
):
    """Get quantity for a specific product."""
    quantity = service.get_total_quantity(product_id)
    return {"product_id": product_id, "quantity": quantity}
