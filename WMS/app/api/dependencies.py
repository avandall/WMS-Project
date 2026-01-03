"""
Dependency injection for PMKT API services.
Provides per-request PostgreSQL-backed repositories and services.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.repositories.interfaces.interfaces import (
    IDocumentRepo,
    IInventoryRepo,
    IProductRepo,
    IWarehouseRepo,
)
from app.repositories.sql.document_repo import DocumentRepo
from app.repositories.sql.inventory_repo import InventoryRepo
from app.repositories.sql.product_repo import ProductRepo
from app.repositories.sql.warehouse_repo import WarehouseRepo
from app.services.document_service import DocumentService
from app.services.inventory_service import InventoryService
from app.services.product_service import ProductService
from app.services.report_service import ReportService
from app.services.warehouse_operations_service import WarehouseOperationsService
from app.services.warehouse_service import WarehouseService


def get_product_repo(db: Session = Depends(get_session)) -> IProductRepo:
    """Provide a product repository bound to the current DB session."""
    return ProductRepo(db)


def get_inventory_repo(db: Session = Depends(get_session)) -> IInventoryRepo:
    """Provide an inventory repository bound to the current DB session."""
    return InventoryRepo(db)


def get_warehouse_repo(db: Session = Depends(get_session)) -> IWarehouseRepo:
    """Provide a warehouse repository bound to the current DB session."""
    return WarehouseRepo(db)


def get_document_repo(db: Session = Depends(get_session)) -> IDocumentRepo:
    """Provide a document repository bound to the current DB session."""
    return DocumentRepo(db)


def get_product_service(db: Session = Depends(get_session)) -> ProductService:
    product_repo = ProductRepo(db)
    inventory_repo = InventoryRepo(db)
    return ProductService(product_repo=product_repo, inventory_repo=inventory_repo)


def get_inventory_service(db: Session = Depends(get_session)) -> InventoryService:
    inventory_repo = InventoryRepo(db)
    product_repo = ProductRepo(db)
    warehouse_repo = WarehouseRepo(db)
    return InventoryService(
        inventory_repo=inventory_repo,
        product_repo=product_repo,
        warehouse_repo=warehouse_repo,
    )


def get_warehouse_service(db: Session = Depends(get_session)) -> WarehouseService:
    warehouse_repo = WarehouseRepo(db)
    product_repo = ProductRepo(db)
    inventory_repo = InventoryRepo(db)
    return WarehouseService(
        warehouse_repo=warehouse_repo,
        product_repo=product_repo,
        inventory_repo=inventory_repo,
    )


def get_document_service(db: Session = Depends(get_session)) -> DocumentService:
    document_repo = DocumentRepo(db)
    warehouse_repo = WarehouseRepo(db)
    product_repo = ProductRepo(db)
    inventory_repo = InventoryRepo(db)
    return DocumentService(
        document_repo=document_repo,
        warehouse_repo=warehouse_repo,
        product_repo=product_repo,
        inventory_repo=inventory_repo,
    )


def get_report_service(db: Session = Depends(get_session)) -> ReportService:
    product_repo = ProductRepo(db)
    document_repo = DocumentRepo(db)
    warehouse_repo = WarehouseRepo(db)
    inventory_repo = InventoryRepo(db)
    return ReportService(product_repo, document_repo, warehouse_repo, inventory_repo)


def get_warehouse_operations_service(
    db: Session = Depends(get_session),
) -> WarehouseOperationsService:
    warehouse_repo = WarehouseRepo(db)
    product_repo = ProductRepo(db)
    inventory_repo = InventoryRepo(db)
    document_repo = DocumentRepo(db)
    return WarehouseOperationsService(
        warehouse_repo=warehouse_repo,
        product_repo=product_repo,
        inventory_repo=inventory_repo,
        document_repo=document_repo,
    )
