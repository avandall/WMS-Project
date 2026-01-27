"""
Warehouses API router.
Provides endpoints for warehouse management operations.
"""

from fastapi import APIRouter, Depends
from ..dependencies import get_warehouse_service
from ..schemas.product import (
    WarehouseCreate,
    WarehouseResponse,
    InventoryItemResponse,
    TransferInventoryRequest,
    WarehouseTransferResponse,
)
from app.services.warehouse_service import WarehouseService

router = APIRouter()


@router.get("/", response_model=list[WarehouseResponse])
async def get_all_warehouses(service: WarehouseService = Depends(get_warehouse_service)):
    """Get all warehouses."""
    warehouses = service.get_all_warehouses()
    result = []
    for warehouse in warehouses:
        inventory = service.get_warehouse_inventory(warehouse.warehouse_id)
        result.append(WarehouseResponse(
            warehouse_id=warehouse.warehouse_id,
            location=warehouse.location,
            inventory=[InventoryItemResponse.from_domain(item) for item in inventory],
        ))
    return result


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


@router.post("/{warehouse_id}/transfer", response_model=WarehouseTransferResponse)
async def transfer_all_inventory(
    warehouse_id: int,
    transfer_request: TransferInventoryRequest,
    service: WarehouseService = Depends(get_warehouse_service),
):
    """
    Transfer all inventory from one warehouse to another.

    This is useful when you need to:
    - Empty a warehouse before deletion
    - Consolidate inventory from multiple warehouses
    - Relocate stock due to warehouse closure or reorganization

    All products and quantities will be moved from the source warehouse
    to the destination warehouse in a single atomic operation.
    """
    transferred_items = service.transfer_all_inventory(
        warehouse_id, transfer_request.to_warehouse_id
    )

    return WarehouseTransferResponse(
        from_warehouse_id=warehouse_id,
        to_warehouse_id=transfer_request.to_warehouse_id,
        transferred_items=[
            InventoryItemResponse.from_domain(item) for item in transferred_items
        ],
        message=f"Successfully transferred {len(transferred_items)} product(s) from warehouse {warehouse_id} to {transfer_request.to_warehouse_id}",
    )


# NOTE: Inventory changes must be performed through document endpoints (import/export/transfer)
# to ensure consistent business rules and pricing. No direct add/remove routes are exposed here.
