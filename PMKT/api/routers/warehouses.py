"""
Warehouses API router.
Provides endpoints for warehouse management operations.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from ..dependencies import get_warehouse_service
from ..models import WarehouseCreate, WarehouseResponse, InventoryItemResponse, ProductMovement
from PMKT.services.warehouse_service import WarehouseService
from PMKT.module.custom_exceptions import WarehouseNotFoundError

router = APIRouter()

@router.post("/", response_model=WarehouseResponse)
async def create_warehouse(
    warehouse: WarehouseCreate,
    service: WarehouseService = Depends(get_warehouse_service)
):
    """Create a new warehouse."""
    try:
        created_warehouse = service.create_warehouse(warehouse.location)
        return WarehouseResponse.from_domain(created_warehouse)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: int,
    service: WarehouseService = Depends(get_warehouse_service)
):
    """Get warehouse information."""
    try:
        warehouse = service.get_warehouse(warehouse_id)
        inventory = service.get_warehouse_inventory(warehouse_id)
        return WarehouseResponse(
            warehouse_id=warehouse.warehouse_id,
            location=warehouse.location,
            inventory=[InventoryItemResponse.from_domain(item) for item in inventory]
        )
    except WarehouseNotFoundError:
        raise HTTPException(status_code=404, detail=f"Warehouse {warehouse_id} not found")

@router.post("/{warehouse_id}/products")
async def add_product_to_warehouse(
    warehouse_id: int,
    movement: ProductMovement,
    service: WarehouseService = Depends(get_warehouse_service)
):
    """Add product to warehouse."""
    try:
        service.add_product_to_warehouse(
            warehouse_id=warehouse_id,
            product_id=movement.product_id,
            quantity=movement.quantity
        )
        return {"message": f"Added {movement.quantity} of product {movement.product_id} to warehouse {warehouse_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{warehouse_id}/products")
async def remove_product_from_warehouse(
    warehouse_id: int,
    movement: ProductMovement,
    service: WarehouseService = Depends(get_warehouse_service)
):
    """Remove product from warehouse."""
    try:
        service.remove_product_from_warehouse(
            warehouse_id=warehouse_id,
            product_id=movement.product_id,
            quantity=movement.quantity
        )
        return {"message": f"Removed {movement.quantity} of product {movement.product_id} from warehouse {warehouse_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))