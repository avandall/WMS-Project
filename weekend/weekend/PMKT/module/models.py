"""
Data Transfer Objects (DTOs) for PMKT Warehouse Management System.
These are simple data containers without business logic.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class Product(BaseModel):
    """DTO for Product data."""
    product_id: int
    name: str
    description: Optional[str] = None
    price: float = Field(default=0.0, ge=0)


class InventoryItem(BaseModel):
    """DTO for Inventory Item data."""
    product_id: int
    quantity: int = Field(default=0, ge=0)


class Warehouse(BaseModel):
    """DTO for Warehouse data."""
    warehouse_id: int
    location: str
    inventory: List[InventoryItem] = Field(default_factory=list)


class DocumentType(str, Enum):
    """Enumeration for document types."""
    IMPORT = "IMPORT"   # Nhập
    EXPORT = "EXPORT"   # Xuất
    TRANSFER = "TRANSFER"  # Chuyển kho


class DocumentStatus(str, Enum):
    """Enumeration for document statuses."""
    DRAFT = "DRAFT"      # Nháp
    POSTED = "POSTED"    # Đã xác nhận (Không được sửa)
    CANCELLED = "CANCELLED"  # Đã hủy


class DocumentProduct(BaseModel):
    """DTO for Document Product data."""
    product_id: int
    quantity: int = Field(gt=0)
    unit_price: float = Field(ge=0)  # Giá tại thời điểm nhập/xuất


class Document(BaseModel):
    """DTO for Document data."""
    document_id: int
    doc_type: DocumentType
    status: DocumentStatus = DocumentStatus.DRAFT
    date: datetime = Field(default_factory=datetime.now)
    from_warehouse_id: Optional[int] = None  # Dùng cho Xuất/Chuyển
    to_warehouse_id: Optional[int] = None    # Dùng cho Nhập/Chuyển
    items: List[DocumentProduct] = Field(default_factory=list)
    created_by: str
    note: Optional[str] = None
    approved_by: Optional[str] = None  
