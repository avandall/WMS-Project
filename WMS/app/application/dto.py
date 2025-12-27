"""
Data Transfer Objects for the Application Layer.
These DTOs are used for communication between layers.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.document_domain import DocumentType, DocumentStatus


# Product DTOs
class ProductDTO(BaseModel):
    """DTO for Product data transfer."""
    product_id: int
    name: str
    price: float
    description: Optional[str] = None

    class Config:
        from_attributes = True


class CreateProductDTO(BaseModel):
    """DTO for creating a new product."""
    product_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., ge=0)
    description: Optional[str] = Field(None, max_length=500)


class UpdateProductDTO(BaseModel):
    """DTO for updating an existing product."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=500)


# Inventory DTOs
class InventoryItemDTO(BaseModel):
    """DTO for inventory item data transfer."""
    product_id: int
    quantity: int

    class Config:
        from_attributes = True


class InventoryStatusDTO(BaseModel):
    """DTO for comprehensive inventory status."""
    product: ProductDTO
    total_quantity: int
    allocated_quantity: int
    unallocated_quantity: int
    warehouse_count: int
    warehouse_distribution: List[dict]


# Warehouse DTOs
class WarehouseDTO(BaseModel):
    """DTO for warehouse data transfer."""
    warehouse_id: int
    location: str
    inventory: List[InventoryItemDTO] = Field(default_factory=list)

    class Config:
        from_attributes = True


class CreateWarehouseDTO(BaseModel):
    """DTO for creating a new warehouse."""
    location: str = Field(..., min_length=1, max_length=200)


class WarehouseInventoryDTO(BaseModel):
    """DTO for warehouse inventory with enriched product data."""
    product: ProductDTO
    quantity: int
    warehouse_id: int


# Document DTOs
class DocumentProductDTO(BaseModel):
    """DTO for document product data."""
    product_id: int
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


class DocumentDTO(BaseModel):
    """DTO for document data transfer."""
    document_id: int
    doc_type: DocumentType
    status: DocumentStatus
    from_warehouse_id: Optional[int] = None
    to_warehouse_id: Optional[int] = None
    items: List[DocumentProductDTO] = Field(default_factory=list)
    created_by: str
    date: datetime

    class Config:
        from_attributes = True


class CreateDocumentDTO(BaseModel):
    """DTO for creating a new document."""
    doc_type: DocumentType
    from_warehouse_id: Optional[int] = None
    to_warehouse_id: Optional[int] = None
    items: List[dict] = Field(..., min_items=1)  # List of {"product_id": int, "quantity": int, "unit_price": float}
    created_by: str = Field(..., min_length=1, max_length=100)
    note: Optional[str] = Field(None, max_length=500)


# Report DTOs
class ProductReportDTO(BaseModel):
    """DTO for product reports."""
    product_id: int
    name: str
    total_quantity: int
    total_value: float
    warehouses: List[dict]  # [{"warehouse_id": int, "location": str, "quantity": int}]


class WarehouseReportDTO(BaseModel):
    """DTO for warehouse reports."""
    warehouse_id: int
    location: str
    total_products: int
    total_value: float
    products: List[dict]  # [{"product_id": int, "name": str, "quantity": int, "value": float}]


class InventoryReportDTO(BaseModel):
    """DTO for comprehensive inventory reports."""
    total_products: int
    total_warehouses: int
    total_inventory_value: float
    low_stock_products: List[dict]
    out_of_stock_products: List[dict]