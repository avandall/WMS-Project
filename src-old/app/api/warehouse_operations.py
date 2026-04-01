"""
Warehouse Operations API router.
Provides endpoints for complex warehouse operations.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from .dependencies import get_warehouse_operations_service
from app.services.warehouse_operations_service import WarehouseOperationsService

router = APIRouter()


@router.get("/system-overview")
async def get_system_overview(
    service: WarehouseOperationsService = Depends(get_warehouse_operations_service),
):
    """Get comprehensive overview of the entire warehouse system."""
    return service.get_system_overview()


@router.get("/inventory-health")
async def get_inventory_health_report(
    service: WarehouseOperationsService = Depends(get_warehouse_operations_service),
):
    """Generate comprehensive inventory health report across all warehouses."""
    return service.get_inventory_health_report()


@router.get("/optimize-distribution/{product_id}")
async def optimize_inventory_distribution(
    product_id: int,
    service: WarehouseOperationsService = Depends(get_warehouse_operations_service),
):
    """Analyze and suggest optimal inventory distribution for a product."""
    result = service.optimize_inventory_distribution(product_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/bulk-transfer")
async def bulk_transfer_products(
    transfers: List[Dict[str, Any]],
    service: WarehouseOperationsService = Depends(get_warehouse_operations_service),
):
    """Execute bulk transfer operations across multiple products/warehouses."""
    return service.bulk_transfer_products(transfers)
