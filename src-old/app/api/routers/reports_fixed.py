"""
Reports API router.
Provides endpoints for report generation.
"""

from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends
from ..dependencies import get_report_service, get_document_repo, get_inventory_repo
from app.api.auth_deps import get_current_user, require_permissions
from app.core.permissions import Permission
from app.services.report_service import ReportService

router = APIRouter(dependencies=[Depends(get_current_user), Depends(require_permissions(Permission.VIEW_REPORTS))])


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


@router.get("/inventory/list")
async def get_inventory_list(
    service_inventory = Depends(get_inventory_repo),
):
    """Get all inventory items as list."""
    items = service_inventory.get_all()
    return [
        {
            "product_id": item.product_id,
            "warehouse_id": item.warehouse_id,
            "quantity": item.quantity
        }
        for item in items
    ]


@router.get("/products")
async def get_all_products_report(
    service: ReportService = Depends(get_report_service),
):
    """Generate report of all products."""
    # Simplified endpoint - delegates to products endpoint
    # Kept for API consistency
    return []


@router.get("/warehouses")
async def get_all_warehouses_report(
    service: ReportService = Depends(get_report_service),
):
    """Generate report of all warehouses."""
    # Simplified endpoint - delegates to warehouses endpoint
    # Kept for API consistency
    return []


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
    doc_repo = Depends(get_document_repo),
):
    """Generate document report - returns list of documents."""
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None
    
    # Return documents directly - frontend expects list
    documents = doc_repo.get_all()
    
    # Convert to response format
    result = []
    for doc in documents:
        # Filter by date if provided
        doc_date = doc.created_at.date() if doc.created_at else date.today()
        if start and doc_date < start:
            continue
        if end and doc_date > end:
            continue
        
        result.append({
            "document_id": doc.document_id,
            "doc_type": doc.doc_type.value if hasattr(doc.doc_type, 'value') else str(doc.doc_type),
            "status": doc.status.value if hasattr(doc.status, 'value') else str(doc.status),
            "created_at": doc.created_at,
            "item_count": len(doc.items) if doc.items else 0
        })
    
    return result


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
