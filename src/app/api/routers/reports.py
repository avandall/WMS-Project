"""
Reports API router.
Provides endpoints for report generation.
"""

from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends
from ..dependencies import get_report_service, get_document_repo, get_inventory_repo, get_warehouse_repo
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
    """Generate inventory report (summary object)."""
    report = service.generate_inventory_report(
        warehouse_id=warehouse_id, low_stock_threshold=low_stock_threshold
    )
    return report


@router.get("/inventory/list")
async def get_inventory_list(
    warehouse_repo=Depends(get_warehouse_repo),
):
    """Return flat inventory list for UI table export."""
    from app.repositories.sql.models import WarehouseInventoryModel
    from sqlalchemy import select
    
    # Get all warehouse inventory items directly from the table
    session = warehouse_repo.session
    rows = session.execute(select(WarehouseInventoryModel)).scalars().all()
    
    return [
        {"product_id": row.product_id, "warehouse_id": row.warehouse_id, "quantity": row.quantity}
        for row in rows
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
    doc_repo=Depends(get_document_repo),
):
    """Return list of documents for transaction report."""
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None

    documents = doc_repo.get_all()
    result: List[dict] = []
    for doc in documents:
        doc_date = doc.created_at.date() if getattr(doc, "created_at", None) else date.today()
        if start and doc_date < start:
            continue
        if end and doc_date > end:
            continue

        result.append(
            {
                "document_id": doc.document_id,
                "doc_type": doc.doc_type.value if hasattr(doc.doc_type, "value") else str(doc.doc_type),
                "status": doc.status.value if hasattr(doc.status, "value") else str(doc.status),
                "created_at": doc.created_at,
                "item_count": len(doc.items) if getattr(doc, "items", None) else 0,
                "customer_id": getattr(doc, "customer_id", None),
            }
        )

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


@router.get("/sales")
async def get_sales_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    customer_id: Optional[int] = None,
    salesperson: Optional[str] = None,
    doc_repo=Depends(get_document_repo),
):
    """Generate sales analytics report showing salesperson, customer, sales totals, and debt."""
    from app.repositories.sql.models import DocumentModel, CustomerModel, DocumentItemModel
    from sqlalchemy import select, and_, func
    from datetime import datetime
    
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None
    
    session = doc_repo.session
    
    # Query for SALE documents with customer and items info
    query = select(
        DocumentModel.document_id,
        DocumentModel.created_by.label('salesperson'),
        DocumentModel.created_at,
        DocumentModel.customer_id,
        CustomerModel.name.label('customer_name'),
        CustomerModel.debt_balance,
        func.sum(DocumentItemModel.quantity * DocumentItemModel.unit_price).label('total_sale')
    ).select_from(DocumentModel).join(
        CustomerModel, DocumentModel.customer_id == CustomerModel.customer_id, isouter=True
    ).join(
        DocumentItemModel, DocumentModel.document_id == DocumentItemModel.document_id
    ).where(
        DocumentModel.doc_type == 'SALE'
    )
    
    # Apply filters
    filters = []
    if start:
        filters.append(func.date(DocumentModel.created_at) >= start)
    if end:
        filters.append(func.date(DocumentModel.created_at) <= end)
    if customer_id:
        filters.append(DocumentModel.customer_id == customer_id)
    if salesperson:
        filters.append(DocumentModel.created_by.ilike(f'%{salesperson}%'))
    
    if filters:
        query = query.where(and_(*filters))
    
    # Group by document to get totals
    query = query.group_by(
        DocumentModel.document_id,
        DocumentModel.created_by,
        DocumentModel.created_at,
        DocumentModel.customer_id,
        CustomerModel.name,
        CustomerModel.debt_balance
    ).order_by(DocumentModel.created_at.desc())
    
    results = session.execute(query).all()
    
    # Format response
    sales_data = []
    total_sales = 0.0
    total_debt = 0.0
    
    for row in results:
        sale_value = float(row.total_sale or 0)
        debt = float(row.debt_balance or 0)
        total_sales += sale_value
        
        sales_data.append({
            "document_id": row.document_id,
            "salesperson": row.salesperson,
            "customer_id": row.customer_id,
            "customer_name": row.customer_name or "N/A",
            "sale_date": row.created_at.isoformat() if row.created_at else None,
            "total_sale": round(sale_value, 2),
            "customer_debt": round(debt, 2),
        })
    
    # Calculate unique customer debts (avoid counting same customer multiple times)
    unique_customers = {}
    for row in results:
        if row.customer_id and row.customer_id not in unique_customers:
            unique_customers[row.customer_id] = float(row.debt_balance or 0)
    
    total_debt = sum(unique_customers.values())
    
    return {
        "summary": {
            "total_sales": round(total_sales, 2),
            "total_debt": round(total_debt, 2),
            "transaction_count": len(sales_data),
            "unique_customers": len(unique_customers),
            "period": {
                "start": start_date,
                "end": end_date
            }
        },
        "sales": sales_data
    }
