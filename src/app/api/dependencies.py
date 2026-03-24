"""
Dependency injection for PMKT API services.
Provides per-request PostgreSQL-backed repositories and services.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.application.ports import (
    IDocumentRepo,
    IInventoryRepo,
    IProductRepo,
    IWarehouseRepo,
    ICustomerRepo,
)
from app.infrastructure.persistence.sql import (
    CustomerRepo,
    DocumentRepo,
    InventoryRepo,
    ProductRepo,
    WarehouseRepo,
)
from app.application.services import (
    DocumentService,
    InventoryService,
    ProductService,
    ReportService,
    WarehouseOperationsService,
    WarehouseService,
)


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


def get_customer_repo(db: Session = Depends(get_session)) -> ICustomerRepo:
    """Provide a customer repository bound to the current DB session."""
    return CustomerRepo(db)


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
    customer_repo = CustomerRepo(db)
    return DocumentService(
        document_repo=document_repo,
        warehouse_repo=warehouse_repo,
        product_repo=product_repo,
        inventory_repo=inventory_repo,
        customer_repo=customer_repo,
        session=db,  # Pass session for transaction management
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
