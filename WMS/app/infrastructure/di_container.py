"""
Dependency Injection Container for the Infrastructure Layer.
Provides proper dependency injection instead of singletons.
"""

from typing import Protocol
from app.repositories.sql.product_repo import ProductRepo
from app.repositories.sql.warehouse_repo import WarehouseRepo
from app.repositories.sql.inventory_repo import InventoryRepo
from app.repositories.sql.document_repo import DocumentRepo
from app.services.product_service import ProductService
from app.services.warehouse_service import WarehouseService
from app.services.inventory_service import InventoryService
from app.services.document_service import DocumentService
from app.services.report_service import ReportService
from app.application.command_handlers import (
    CreateProductHandler, UpdateProductHandler, DeleteProductHandler,
    CreateWarehouseHandler, UpdateWarehouseHandler, DeleteWarehouseHandler,
    AddInventoryHandler, RemoveInventoryHandler, TransferInventoryHandler,
    CreateDocumentHandler, ProcessDocumentHandler, CancelDocumentHandler
)
from app.application.query_handlers import (
    GetProductHandler, GetAllProductsHandler, GetProductsByIdsHandler,
    GetWarehouseHandler, GetAllWarehousesHandler, GetWarehouseInventoryHandler,
    GetProductInventoryHandler, GetInventoryStatusHandler,
    GetDocumentHandler, GetDocumentsHandler,
    GetProductReportHandler, GetWarehouseReportHandler, GetInventoryReportHandler
)


class DIContainer:
    """Dependency Injection Container."""

    def __init__(self):
        # Repositories
        self._product_repository = None
        self._warehouse_repository = None
        self._inventory_repository = None
        self._document_repository = None

        # Services
        self._product_service = None
        self._warehouse_service = None
        self._inventory_service = None
        self._document_service = None
        self._report_service = None

        # Command Handlers
        self._command_handlers = {}

        # Query Handlers
        self._query_handlers = {}

    # Repository providers
    @property
    def product_repository(self) -> ProductRepo:
        if self._product_repository is None:
            self._product_repository = ProductRepo()
        return self._product_repository

    @property
    def warehouse_repository(self) -> WarehouseRepo:
        if self._warehouse_repository is None:
            self._warehouse_repository = WarehouseRepo()
        return self._warehouse_repository

    @property
    def inventory_repository(self) -> InventoryRepo:
        if self._inventory_repository is None:
            self._inventory_repository = InventoryRepo()
        return self._inventory_repository

    @property
    def document_repository(self) -> DocumentRepo:
        if self._document_repository is None:
            self._document_repository = DocumentRepo()
        return self._document_repository

    # Service providers
    @property
    def product_service(self) -> ProductService:
        if self._product_service is None:
            self._product_service = ProductService(self.product_repository)
        return self._product_service

    @property
    def warehouse_service(self) -> WarehouseService:
        if self._warehouse_service is None:
            self._warehouse_service = WarehouseService(self.warehouse_repository)
        return self._warehouse_service

    @property
    def inventory_service(self) -> InventoryService:
        if self._inventory_service is None:
            self._inventory_service = InventoryService(
                self.inventory_repository,
                self.product_repository,
                self.warehouse_repository
            )
        return self._inventory_service

    @property
    def document_service(self) -> DocumentService:
        if self._document_service is None:
            self._document_service = DocumentService(
                self.document_repository,
                self.inventory_service
            )
        return self._document_service

    @property
    def report_service(self) -> ReportService:
        if self._report_service is None:
            self._report_service = ReportService(
                self.product_repository,
                self.warehouse_repository,
                self.inventory_repository
            )
        return self._report_service

    # Command Handler providers
    def get_create_product_handler(self) -> CreateProductHandler:
        if 'create_product' not in self._command_handlers:
            self._command_handlers['create_product'] = CreateProductHandler(self.product_service)
        return self._command_handlers['create_product']

    def get_update_product_handler(self) -> UpdateProductHandler:
        if 'update_product' not in self._command_handlers:
            self._command_handlers['update_product'] = UpdateProductHandler(self.product_service)
        return self._command_handlers['update_product']

    def get_delete_product_handler(self) -> DeleteProductHandler:
        if 'delete_product' not in self._command_handlers:
            self._command_handlers['delete_product'] = DeleteProductHandler(self.product_service)
        return self._command_handlers['delete_product']

    def get_create_warehouse_handler(self) -> CreateWarehouseHandler:
        if 'create_warehouse' not in self._command_handlers:
            self._command_handlers['create_warehouse'] = CreateWarehouseHandler(self.warehouse_service)
        return self._command_handlers['create_warehouse']

    def get_update_warehouse_handler(self) -> UpdateWarehouseHandler:
        if 'update_warehouse' not in self._command_handlers:
            self._command_handlers['update_warehouse'] = UpdateWarehouseHandler(self.warehouse_service)
        return self._command_handlers['update_warehouse']

    def get_delete_warehouse_handler(self) -> DeleteWarehouseHandler:
        if 'delete_warehouse' not in self._command_handlers:
            self._command_handlers['delete_warehouse'] = DeleteWarehouseHandler(self.warehouse_service)
        return self._command_handlers['delete_warehouse']

    def get_add_inventory_handler(self) -> AddInventoryHandler:
        if 'add_inventory' not in self._command_handlers:
            self._command_handlers['add_inventory'] = AddInventoryHandler(self.inventory_service)
        return self._command_handlers['add_inventory']

    def get_remove_inventory_handler(self) -> RemoveInventoryHandler:
        if 'remove_inventory' not in self._command_handlers:
            self._command_handlers['remove_inventory'] = RemoveInventoryHandler(self.inventory_service)
        return self._command_handlers['remove_inventory']

    def get_transfer_inventory_handler(self) -> TransferInventoryHandler:
        if 'transfer_inventory' not in self._command_handlers:
            self._command_handlers['transfer_inventory'] = TransferInventoryHandler(self.inventory_service)
        return self._command_handlers['transfer_inventory']

    def get_create_document_handler(self) -> CreateDocumentHandler:
        if 'create_document' not in self._command_handlers:
            self._command_handlers['create_document'] = CreateDocumentHandler(self.document_service)
        return self._command_handlers['create_document']

    def get_process_document_handler(self) -> ProcessDocumentHandler:
        if 'process_document' not in self._command_handlers:
            self._command_handlers['process_document'] = ProcessDocumentHandler(self.document_service)
        return self._command_handlers['process_document']

    def get_cancel_document_handler(self) -> CancelDocumentHandler:
        if 'cancel_document' not in self._command_handlers:
            self._command_handlers['cancel_document'] = CancelDocumentHandler(self.document_service)
        return self._command_handlers['cancel_document']

    # Query Handler providers
    def get_product_handler(self) -> GetProductHandler:
        if 'get_product' not in self._query_handlers:
            self._query_handlers['get_product'] = GetProductHandler(self.product_service)
        return self._query_handlers['get_product']

    def get_all_products_handler(self) -> GetAllProductsHandler:
        if 'get_all_products' not in self._query_handlers:
            self._query_handlers['get_all_products'] = GetAllProductsHandler(self.product_service)
        return self._query_handlers['get_all_products']

    def get_products_by_ids_handler(self) -> GetProductsByIdsHandler:
        if 'get_products_by_ids' not in self._query_handlers:
            self._query_handlers['get_products_by_ids'] = GetProductsByIdsHandler(self.product_service)
        return self._query_handlers['get_products_by_ids']

    def get_warehouse_handler(self) -> GetWarehouseHandler:
        if 'get_warehouse' not in self._query_handlers:
            self._query_handlers['get_warehouse'] = GetWarehouseHandler(self.warehouse_service)
        return self._query_handlers['get_warehouse']

    def get_all_warehouses_handler(self) -> GetAllWarehousesHandler:
        if 'get_all_warehouses' not in self._query_handlers:
            self._query_handlers['get_all_warehouses'] = GetAllWarehousesHandler(self.warehouse_service)
        return self._query_handlers['get_all_warehouses']

    def get_warehouse_inventory_handler(self) -> GetWarehouseInventoryHandler:
        if 'get_warehouse_inventory' not in self._query_handlers:
            self._query_handlers['get_warehouse_inventory'] = GetWarehouseInventoryHandler(self.warehouse_service)
        return self._query_handlers['get_warehouse_inventory']

    def get_product_inventory_handler(self) -> GetProductInventoryHandler:
        if 'get_product_inventory' not in self._query_handlers:
            self._query_handlers['get_product_inventory'] = GetProductInventoryHandler(self.inventory_service)
        return self._query_handlers['get_product_inventory']

    def get_inventory_status_handler(self) -> GetInventoryStatusHandler:
        if 'get_inventory_status' not in self._query_handlers:
            self._query_handlers['get_inventory_status'] = GetInventoryStatusHandler(self.inventory_service)
        return self._query_handlers['get_inventory_status']

    def get_document_handler(self) -> GetDocumentHandler:
        if 'get_document' not in self._query_handlers:
            self._query_handlers['get_document'] = GetDocumentHandler(self.document_service)
        return self._query_handlers['get_document']

    def get_documents_handler(self) -> GetDocumentsHandler:
        if 'get_documents' not in self._query_handlers:
            self._query_handlers['get_documents'] = GetDocumentsHandler(self.document_service)
        return self._query_handlers['get_documents']

    def get_product_report_handler(self) -> GetProductReportHandler:
        if 'get_product_report' not in self._query_handlers:
            self._query_handlers['get_product_report'] = GetProductReportHandler(self.report_service)
        return self._query_handlers['get_product_report']

    def get_warehouse_report_handler(self) -> GetWarehouseReportHandler:
        if 'get_warehouse_report' not in self._query_handlers:
            self._query_handlers['get_warehouse_report'] = GetWarehouseReportHandler(self.report_service)
        return self._query_handlers['get_warehouse_report']

    def get_inventory_report_handler(self) -> GetInventoryReportHandler:
        if 'get_inventory_report' not in self._query_handlers:
            self._query_handlers['get_inventory_report'] = GetInventoryReportHandler(self.report_service)
        return self._query_handlers['get_inventory_report']


# Global container instance
_container = None

def get_container() -> DIContainer:
    """Get the global DI container instance."""
    global _container
    if _container is None:
        _container = DIContainer()
    return _container