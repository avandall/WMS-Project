"""
Query objects for the Application Layer.
Queries represent read operations in CQRS pattern.
"""

from typing import List, Optional
from dataclasses import dataclass
from app.application.dto import (
    ProductDTO, InventoryItemDTO, WarehouseDTO, DocumentDTO,
    ProductReportDTO, WarehouseReportDTO, InventoryReportDTO
)


# Product Queries
@dataclass(frozen=True)
class GetProductQuery:
    """Query to get a single product."""
    product_id: int


@dataclass(frozen=True)
class GetAllProductsQuery:
    """Query to get all products."""
    skip: int = 0
    limit: int = 100
    search: Optional[str] = None


@dataclass(frozen=True)
class GetProductsByIdsQuery:
    """Query to get multiple products by IDs."""
    product_ids: List[int]


# Warehouse Queries
@dataclass(frozen=True)
class GetWarehouseQuery:
    """Query to get a single warehouse."""
    warehouse_id: int


@dataclass(frozen=True)
class GetAllWarehousesQuery:
    """Query to get all warehouses."""
    skip: int = 0
    limit: int = 100


@dataclass(frozen=True)
class GetWarehouseInventoryQuery:
    """Query to get inventory for a specific warehouse."""
    warehouse_id: int
    product_id: Optional[int] = None


# Inventory Queries
@dataclass(frozen=True)
class GetProductInventoryQuery:
    """Query to get inventory status for a product across all warehouses."""
    product_id: int


@dataclass(frozen=True)
class GetInventoryStatusQuery:
    """Query to get comprehensive inventory status."""
    warehouse_id: Optional[int] = None
    product_id: Optional[int] = None
    low_stock_threshold: Optional[int] = None


@dataclass(frozen=True)
class GetLowStockProductsQuery:
    """Query to get products with low stock."""
    threshold: int = 10


@dataclass(frozen=True)
class GetOutOfStockProductsQuery:
    """Query to get products that are out of stock."""


# Document Queries
@dataclass(frozen=True)
class GetDocumentQuery:
    """Query to get a single document."""
    document_id: int


@dataclass(frozen=True)
class GetDocumentsQuery:
    """Query to get documents with filtering."""
    doc_type: Optional[str] = None
    status: Optional[str] = None
    warehouse_id: Optional[int] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    skip: int = 0
    limit: int = 100


@dataclass(frozen=True)
class GetPendingDocumentsQuery:
    """Query to get documents pending processing."""
    warehouse_id: Optional[int] = None


# Report Queries
@dataclass(frozen=True)
class GetProductReportQuery:
    """Query to get product report."""
    product_id: Optional[int] = None


@dataclass(frozen=True)
class GetWarehouseReportQuery:
    """Query to get warehouse report."""
    warehouse_id: Optional[int] = None


@dataclass(frozen=True)
class GetInventoryReportQuery:
    """Query to get comprehensive inventory report."""
    include_low_stock: bool = True
    include_out_of_stock: bool = True


# Query Results
@dataclass(frozen=True)
class QueryResult:
    """Base result for queries."""
    success: bool
    message: str
    data: Optional[dict] = None


@dataclass(frozen=True)
class ProductQueryResult(QueryResult):
    """Result containing product data."""
    product: Optional[ProductDTO] = None
    products: Optional[List[ProductDTO]] = None


@dataclass(frozen=True)
class WarehouseQueryResult(QueryResult):
    """Result containing warehouse data."""
    warehouse: Optional[WarehouseDTO] = None
    warehouses: Optional[List[WarehouseDTO]] = None


@dataclass(frozen=True)
class InventoryQueryResult(QueryResult):
    """Result containing inventory data."""
    inventory: Optional[List[InventoryItemDTO]] = None
    total_quantity: Optional[int] = None


@dataclass(frozen=True)
class DocumentQueryResult(QueryResult):
    """Result containing document data."""
    document: Optional[DocumentDTO] = None
    documents: Optional[List[DocumentDTO]] = None


@dataclass(frozen=True)
class ReportQueryResult(QueryResult):
    """Result containing report data."""
    product_report: Optional[List[ProductReportDTO]] = None
    warehouse_report: Optional[List[WarehouseReportDTO]] = None
    inventory_report: Optional[InventoryReportDTO] = None