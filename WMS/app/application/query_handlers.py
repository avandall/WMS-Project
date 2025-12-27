"""
Query Handlers for the Application Layer.
These handle read operations and return data from repositories.
"""

from typing import List, Optional
from app.application.queries import (
    GetProductQuery, GetAllProductsQuery, GetProductsByIdsQuery,
    GetWarehouseQuery, GetAllWarehousesQuery, GetWarehouseInventoryQuery,
    GetProductInventoryQuery, GetInventoryStatusQuery,
    GetLowStockProductsQuery, GetOutOfStockProductsQuery,
    GetDocumentQuery, GetDocumentsQuery, GetPendingDocumentsQuery,
    GetProductReportQuery, GetWarehouseReportQuery, GetInventoryReportQuery,
    ProductQueryResult, WarehouseQueryResult, InventoryQueryResult,
    DocumentQueryResult, ReportQueryResult
)
from app.services.product_service import ProductService
from app.services.warehouse_service import WarehouseService
from app.services.inventory_service import InventoryService
from app.services.document_service import DocumentService
from app.services.report_service import ReportService
from app.application.dto import (
    ProductDTO, WarehouseDTO, InventoryItemDTO, DocumentDTO,
    ProductReportDTO, WarehouseReportDTO, InventoryReportDTO
)


# Product Query Handlers
class GetProductHandler:
    """Handler for getting a single product."""

    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def handle(self, query: GetProductQuery) -> ProductQueryResult:
        try:
            product = self.product_service.get_product(query.product_id)
            if product:
                product_dto = ProductDTO.from_orm(product)
                return ProductQueryResult(
                    success=True,
                    message="Product retrieved successfully",
                    product=product_dto
                )
            else:
                return ProductQueryResult(
                    success=False,
                    message="Product not found"
                )
        except Exception as e:
            return ProductQueryResult(
                success=False,
                message=f"Failed to retrieve product: {str(e)}"
            )


class GetAllProductsHandler:
    """Handler for getting all products."""

    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def handle(self, query: GetAllProductsQuery) -> ProductQueryResult:
        try:
            products = self.product_service.get_all_products(
                skip=query.skip,
                limit=query.limit,
                search=query.search
            )
            product_dtos = [ProductDTO.from_orm(p) for p in products]
            return ProductQueryResult(
                success=True,
                message="Products retrieved successfully",
                products=product_dtos
            )
        except Exception as e:
            return ProductQueryResult(
                success=False,
                message=f"Failed to retrieve products: {str(e)}"
            )


class GetProductsByIdsHandler:
    """Handler for getting products by IDs."""

    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def handle(self, query: GetProductsByIdsQuery) -> ProductQueryResult:
        try:
            products = self.product_service.get_products_by_ids(query.product_ids)
            product_dtos = [ProductDTO.from_orm(p) for p in products]
            return ProductQueryResult(
                success=True,
                message="Products retrieved successfully",
                products=product_dtos
            )
        except Exception as e:
            return ProductQueryResult(
                success=False,
                message=f"Failed to retrieve products: {str(e)}"
            )


# Warehouse Query Handlers
class GetWarehouseHandler:
    """Handler for getting a single warehouse."""

    def __init__(self, warehouse_service: WarehouseService):
        self.warehouse_service = warehouse_service

    def handle(self, query: GetWarehouseQuery) -> WarehouseQueryResult:
        try:
            warehouse = self.warehouse_service.get_warehouse(query.warehouse_id)
            if warehouse:
                warehouse_dto = WarehouseDTO.from_orm(warehouse)
                return WarehouseQueryResult(
                    success=True,
                    message="Warehouse retrieved successfully",
                    warehouse=warehouse_dto
                )
            else:
                return WarehouseQueryResult(
                    success=False,
                    message="Warehouse not found"
                )
        except Exception as e:
            return WarehouseQueryResult(
                success=False,
                message=f"Failed to retrieve warehouse: {str(e)}"
            )


class GetAllWarehousesHandler:
    """Handler for getting all warehouses."""

    def __init__(self, warehouse_service: WarehouseService):
        self.warehouse_service = warehouse_service

    def handle(self, query: GetAllWarehousesQuery) -> WarehouseQueryResult:
        try:
            warehouses = self.warehouse_service.get_all_warehouses(
                skip=query.skip,
                limit=query.limit
            )
            warehouse_dtos = [WarehouseDTO.from_orm(w) for w in warehouses]
            return WarehouseQueryResult(
                success=True,
                message="Warehouses retrieved successfully",
                warehouses=warehouse_dtos
            )
        except Exception as e:
            return WarehouseQueryResult(
                success=False,
                message=f"Failed to retrieve warehouses: {str(e)}"
            )


class GetWarehouseInventoryHandler:
    """Handler for getting warehouse inventory."""

    def __init__(self, warehouse_service: WarehouseService):
        self.warehouse_service = warehouse_service

    def handle(self, query: GetWarehouseInventoryQuery) -> WarehouseQueryResult:
        try:
            warehouse = self.warehouse_service.get_warehouse_inventory(
                query.warehouse_id,
                query.product_id
            )
            if warehouse:
                warehouse_dto = WarehouseDTO.from_orm(warehouse)
                return WarehouseQueryResult(
                    success=True,
                    message="Warehouse inventory retrieved successfully",
                    warehouse=warehouse_dto
                )
            else:
                return WarehouseQueryResult(
                    success=False,
                    message="Warehouse not found"
                )
        except Exception as e:
            return WarehouseQueryResult(
                success=False,
                message=f"Failed to retrieve warehouse inventory: {str(e)}"
            )


# Inventory Query Handlers
class GetProductInventoryHandler:
    """Handler for getting product inventory across warehouses."""

    def __init__(self, inventory_service: InventoryService):
        self.inventory_service = inventory_service

    def handle(self, query: GetProductInventoryQuery) -> InventoryQueryResult:
        try:
            inventory = self.inventory_service.get_product_inventory(query.product_id)
            inventory_dtos = [InventoryItemDTO.from_orm(i) for i in inventory]
            total_quantity = sum(i.quantity for i in inventory)
            return InventoryQueryResult(
                success=True,
                message="Product inventory retrieved successfully",
                inventory=inventory_dtos,
                total_quantity=total_quantity
            )
        except Exception as e:
            return InventoryQueryResult(
                success=False,
                message=f"Failed to retrieve product inventory: {str(e)}"
            )


class GetInventoryStatusHandler:
    """Handler for getting comprehensive inventory status."""

    def __init__(self, inventory_service: InventoryService):
        self.inventory_service = inventory_service

    def handle(self, query: GetInventoryStatusQuery) -> InventoryQueryResult:
        try:
            status = self.inventory_service.get_inventory_status(
                warehouse_id=query.warehouse_id,
                product_id=query.product_id,
                low_stock_threshold=query.low_stock_threshold
            )
            # Convert to appropriate DTOs based on the status data
            return InventoryQueryResult(
                success=True,
                message="Inventory status retrieved successfully",
                data=status  # This would need proper DTO conversion
            )
        except Exception as e:
            return InventoryQueryResult(
                success=False,
                message=f"Failed to retrieve inventory status: {str(e)}"
            )


# Document Query Handlers
class GetDocumentHandler:
    """Handler for getting a single document."""

    def __init__(self, document_service: DocumentService):
        self.document_service = document_service

    def handle(self, query: GetDocumentQuery) -> DocumentQueryResult:
        try:
            document = self.document_service.get_document(query.document_id)
            if document:
                document_dto = DocumentDTO.from_orm(document)
                return DocumentQueryResult(
                    success=True,
                    message="Document retrieved successfully",
                    document=document_dto
                )
            else:
                return DocumentQueryResult(
                    success=False,
                    message="Document not found"
                )
        except Exception as e:
            return DocumentQueryResult(
                success=False,
                message=f"Failed to retrieve document: {str(e)}"
            )


class GetDocumentsHandler:
    """Handler for getting documents with filtering."""

    def __init__(self, document_service: DocumentService):
        self.document_service = document_service

    def handle(self, query: GetDocumentsQuery) -> DocumentQueryResult:
        try:
            documents = self.document_service.get_documents(
                doc_type=query.doc_type,
                status=query.status,
                warehouse_id=query.warehouse_id,
                date_from=query.date_from,
                date_to=query.date_to,
                skip=query.skip,
                limit=query.limit
            )
            document_dtos = [DocumentDTO.from_orm(d) for d in documents]
            return DocumentQueryResult(
                success=True,
                message="Documents retrieved successfully",
                documents=document_dtos
            )
        except Exception as e:
            return DocumentQueryResult(
                success=False,
                message=f"Failed to retrieve documents: {str(e)}"
            )


# Report Query Handlers
class GetProductReportHandler:
    """Handler for getting product reports."""

    def __init__(self, report_service: ReportService):
        self.report_service = report_service

    def handle(self, query: GetProductReportQuery) -> ReportQueryResult:
        try:
            reports = self.report_service.get_product_report(query.product_id)
            report_dtos = [ProductReportDTO(**r) for r in reports]
            return ReportQueryResult(
                success=True,
                message="Product report retrieved successfully",
                product_report=report_dtos
            )
        except Exception as e:
            return ReportQueryResult(
                success=False,
                message=f"Failed to retrieve product report: {str(e)}"
            )


class GetWarehouseReportHandler:
    """Handler for getting warehouse reports."""

    def __init__(self, report_service: ReportService):
        self.report_service = report_service

    def handle(self, query: GetWarehouseReportQuery) -> ReportQueryResult:
        try:
            reports = self.report_service.get_warehouse_report(query.warehouse_id)
            report_dtos = [WarehouseReportDTO(**r) for r in reports]
            return ReportQueryResult(
                success=True,
                message="Warehouse report retrieved successfully",
                warehouse_report=report_dtos
            )
        except Exception as e:
            return ReportQueryResult(
                success=False,
                message=f"Failed to retrieve warehouse report: {str(e)}"
            )


class GetInventoryReportHandler:
    """Handler for getting comprehensive inventory reports."""

    def __init__(self, report_service: ReportService):
        self.report_service = report_service

    def handle(self, query: GetInventoryReportQuery) -> ReportQueryResult:
        try:
            report = self.report_service.get_inventory_report(
                include_low_stock=query.include_low_stock,
                include_out_of_stock=query.include_out_of_stock
            )
            report_dto = InventoryReportDTO(**report)
            return ReportQueryResult(
                success=True,
                message="Inventory report retrieved successfully",
                inventory_report=report_dto
            )
        except Exception as e:
            return ReportQueryResult(
                success=False,
                message=f"Failed to retrieve inventory report: {str(e)}"
            )