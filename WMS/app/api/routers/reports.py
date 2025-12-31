"""
Reports API router.
Provides endpoints for report generation.
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends
from ..dependencies import get_report_service
from app.services.report_service import ReportService

router = APIRouter()


@router.get("/inventory")
async def get_inventory_report(
    warehouse_id: Optional[int] = None,
    low_stock_threshold: int = 10,
    service: ReportService = Depends(get_report_service),
):
    """Generate inventory report."""
    report = service.generate_inventory_report(
        warehouse_id=warehouse_id, low_stock_threshold=low_stock_threshold
    )
    return report


@router.get("/warehouse/{warehouse_id}")
async def get_warehouse_report(
    warehouse_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    service: ReportService = Depends(get_report_service),
):
    """Generate warehouse performance report."""
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None
    report = service.generate_warehouse_performance_report(
        warehouse_id=warehouse_id, start_date=start, end_date=end
    )
    return report


@router.get("/documents")
async def get_document_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    service: ReportService = Depends(get_report_service),
):
    """Generate document report."""
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None
    # Call generate_business_overview_report since that's what exists
    report = service.generate_business_overview_report(start_date=start, end_date=end)
    return report


@router.get("/product/{product_id}")
async def get_product_report(
    product_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    service: ReportService = Depends(get_report_service),
):
    """Generate product movement report."""
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None
    report = service.generate_product_movement_report(
        product_id=product_id, start_date=start, end_date=end
    )
    return report
