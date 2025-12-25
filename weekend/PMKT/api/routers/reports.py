"""
Reports API router.
Provides endpoints for report generation.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from ..dependencies import get_report_service
from ..models import InventoryReportResponse
from PMKT.services.report_service import ReportService

router = APIRouter()

@router.get("/inventory", response_model=InventoryReportResponse)
async def get_inventory_report(
    warehouse_id: Optional[int] = None,
    low_stock_threshold: int = 10,
    service: ReportService = Depends(get_report_service)
):
    """Generate inventory report."""
    try:
        report = service.generate_inventory_report(
            warehouse_id=warehouse_id,
            low_stock_threshold=low_stock_threshold
        )
        return InventoryReportResponse.from_domain(report)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))