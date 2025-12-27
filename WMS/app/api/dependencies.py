"""
Dependency injection for PMKT API services.
Provides easy access to services and repositories through the container.
"""

from app.core.container import resolve
from app.repositories.interfaces.interfaces import IProductRepo, IInventoryRepo, IWarehouseRepo, IDocumentRepo
from app.services.product_service import ProductService
from app.services.inventory_service import InventoryService
from app.services.warehouse_service import WarehouseService
from app.services.document_service import DocumentService
from app.services.report_service import ReportService
from app.services.warehouse_operations_service import WarehouseOperationsService

# Convenience functions for backward compatibility and easy access

def get_product_repo() -> IProductRepo:
    """Get product repository instance."""
    return resolve(IProductRepo)

def get_inventory_repo() -> IInventoryRepo:
    """Get inventory repository instance."""
    return resolve(IInventoryRepo)

def get_warehouse_repo() -> IWarehouseRepo:
    """Get warehouse repository instance."""
    return resolve(IWarehouseRepo)

def get_document_repo() -> IDocumentRepo:
    """Get document repository instance."""
    return resolve(IDocumentRepo)

def get_product_service() -> ProductService:
    """Get product service instance."""
    return resolve(ProductService)

def get_inventory_service() -> InventoryService:
    """Get inventory service instance."""
    return resolve(InventoryService)

def get_warehouse_service() -> WarehouseService:
    """Get warehouse service instance."""
    return resolve(WarehouseService)

def get_document_service() -> DocumentService:
    """Get document service instance."""
    return resolve(DocumentService)

def get_report_service() -> ReportService:
    """Get report service instance."""
    return resolve(ReportService)

def get_warehouse_operations_service() -> WarehouseOperationsService:
    """Get warehouse operations service instance."""
    return resolve(WarehouseOperationsService)