"""
Warehouses API router.
Provides endpoints for warehouse management operations.
"""

from fastapi import APIRouter, Depends
from ..dependencies import get_warehouse_service
from ..schemas.product import WarehouseCreate, WarehouseResponse, InventoryItemResponse
from app.services.warehouse_service import WarehouseService

router = APIRouter()


@router.post("/", response_model=WarehouseResponse)
async def create_warehouse(
    warehouse: WarehouseCreate,
    service: WarehouseService = Depends(get_warehouse_service),
):
    """Create a new warehouse."""
    created_warehouse = service.create_warehouse(warehouse.location)
    return WarehouseResponse.from_domain(created_warehouse)


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: int, service: WarehouseService = Depends(get_warehouse_service)
):
    """Get warehouse information."""
    warehouse = service.get_warehouse(warehouse_id)
    inventory = service.get_warehouse_inventory(warehouse_id)
    return WarehouseResponse(
        warehouse_id=warehouse.warehouse_id,
        location=warehouse.location,
        inventory=[InventoryItemResponse.from_domain(item) for item in inventory],
    )


@router.delete("/{warehouse_id}")
async def delete_warehouse(
    warehouse_id: int, service: WarehouseService = Depends(get_warehouse_service)
):
    """Delete a warehouse. Only allowed if warehouse has no inventory (stock = 0)."""
    service.delete_warehouse(warehouse_id)
    return {"message": f"Warehouse {warehouse_id} deleted successfully"}


# NOTE: Inventory changes must be performed through document endpoints (import/export/transfer)
# to ensure consistent business rules and pricing. No direct add/remove routes are exposed here.
