"""
Dependency injection for PMKT API services.
Provides singleton instances of services and repositories.
"""

from app.repositories.sql.product_repo import ProductRepo
from app.repositories.sql.inventory_repo import InventoryRepo
from app.repositories.sql.warehouse_repo import WarehouseRepo
from app.repositories.sql.document_repo import DocumentRepo
from app.repositories.interfaces.interfaces import IProductRepo, IInventoryRepo, IWarehouseRepo, IDocumentRepo
from app.services.product_service import ProductService
from app.services.inventory_service import InventoryService
from app.services.warehouse_service import WarehouseService
from app.services.document_service import DocumentService
from app.services.report_service import ReportService
from app.services.warehouse_operations_service import WarehouseOperationsService

# Repository instances (singletons)
_product_repo = None
_inventory_repo = None
_warehouse_repo = None
_document_repo = None

def get_product_repo() -> IProductRepo:
    """Get product repository instance."""
    global _product_repo
    if _product_repo is None:
        _product_repo = ProductRepo()
    return _product_repo

def get_inventory_repo() -> IInventoryRepo:
    """Get inventory repository instance."""
    global _inventory_repo
    if _inventory_repo is None:
        _inventory_repo = InventoryRepo()
    return _inventory_repo

def get_warehouse_repo() -> IWarehouseRepo:
    """Get warehouse repository instance."""
    global _warehouse_repo
    if _warehouse_repo is None:
        _warehouse_repo = WarehouseRepo()
    return _warehouse_repo

def get_document_repo() -> IDocumentRepo:
    """Get document repository instance."""
    global _document_repo
    if _document_repo is None:
        _document_repo = DocumentRepo()
    return _document_repo

# Service instances (singletons)
_product_service = None
_inventory_service = None
_warehouse_service = None
_document_service = None
_report_service = None
_warehouse_operations_service = None

def get_product_service() -> ProductService:
    """Get product service instance."""
    global _product_service
    if _product_service is None:
        _product_service = ProductService(
            product_repo=get_product_repo(),
            inventory_repo=get_inventory_repo()
        )
    return _product_service

def get_inventory_service() -> InventoryService:
    """Get inventory service instance."""
    global _inventory_service
    if _inventory_service is None:
        _inventory_service = InventoryService(
            inventory_repo=get_inventory_repo(),
            product_repo=get_product_repo(),
            warehouse_repo=get_warehouse_repo()
        )
    return _inventory_service

def get_warehouse_service() -> WarehouseService:
    """Get warehouse service instance."""
    global _warehouse_service
    if _warehouse_service is None:
        _warehouse_service = WarehouseService(
            warehouse_repo=get_warehouse_repo(),
            product_repo=get_product_repo(),
            inventory_repo=get_inventory_repo()
        )
    return _warehouse_service

def get_document_service() -> DocumentService:
    """Get document service instance."""
    global _document_service
    if _document_service is None:
        _document_service = DocumentService(
            document_repo=get_document_repo(),
            warehouse_repo=get_warehouse_repo(),
            product_repo=get_product_repo(),
            inventory_repo=get_inventory_repo()
        )
    return _document_service

def get_report_service() -> ReportService:
    """Get report service instance."""
    global _report_service
    if _report_service is None:
        _report_service = ReportService(
            get_product_repo(),
            get_document_repo(),
            get_warehouse_repo(),
            get_inventory_repo()
        )
    return _report_service

def get_warehouse_operations_service() -> WarehouseOperationsService:
    """Get warehouse operations service instance."""
    global _warehouse_operations_service
    if _warehouse_operations_service is None:
        _warehouse_operations_service = WarehouseOperationsService(
            warehouse_repo=get_warehouse_repo(),
            product_repo=get_product_repo(),
            inventory_repo=get_inventory_repo(),
            document_repo=get_document_repo()
        )
    return _warehouse_operations_service