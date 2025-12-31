"""
Pydantic models for API requests and responses.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# Product models
class ProductCreate(BaseModel):
    product_id: int = Field(..., gt=0, description="Unique product identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Product name")
    price: float = Field(
        ...,
        ge=0,
        description="Catalog/list price. Transaction pricing is defined per document item unit_price.",
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Product description"
    )


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(
        None,
        ge=0,
        description="Catalog/list price. Transaction pricing is defined per document item unit_price.",
    )
    description: Optional[str] = Field(None, max_length=500)


class ProductResponse(BaseModel):
    product_id: int
    name: str
    price: float
    description: Optional[str]

    @classmethod
    def from_domain(cls, product):
        return cls(
            product_id=product.product_id,
            name=product.name,
            price=product.price,
            description=product.description,
        )


# Inventory models
class InventoryItemResponse(BaseModel):
    product_id: int
    quantity: int

    @classmethod
    def from_domain(cls, item):
        return cls(product_id=item.product_id, quantity=item.quantity)


# Warehouse models
class WarehouseCreate(BaseModel):
    location: str = Field(
        ..., min_length=1, max_length=200, description="Warehouse location"
    )


class WarehouseResponse(BaseModel):
    warehouse_id: int
    location: str
    inventory: List[InventoryItemResponse]

    @classmethod
    def from_domain(cls, warehouse):
        return cls(
            warehouse_id=warehouse.warehouse_id,
            location=warehouse.location,
            inventory=[
                InventoryItemResponse.from_domain(item) for item in warehouse.inventory
            ],
        )


class ProductMovement(BaseModel):
    product_id: int = Field(..., gt=0, description="Product identifier")
    quantity: int = Field(..., gt=0, description="Quantity to move")


# Document models
class DocumentProductItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)


class DocumentCreate(BaseModel):
    warehouse_id: Optional[int] = Field(
        None, gt=0, description="Target warehouse for import/export"
    )
    from_warehouse_id: Optional[int] = Field(
        None, gt=0, description="Source warehouse for transfer"
    )
    to_warehouse_id: Optional[int] = Field(
        None, gt=0, description="Target warehouse for transfer"
    )
    items: List[DocumentProductItem] = Field(
        ..., min_items=1, description="Document items"
    )
    created_by: str = Field(..., min_length=1, description="Creator name")
    note: Optional[str] = Field(None, description="Optional note")


class DocumentPost(BaseModel):
    approved_by: str = Field(..., min_length=1, description="Approver name")


class DocumentResponse(BaseModel):
    document_id: int
    doc_type: str
    status: str
    from_warehouse_id: Optional[int]
    to_warehouse_id: Optional[int]
    items: List[DocumentProductItem]
    created_by: str
    approved_by: Optional[str]
    date: datetime
    note: Optional[str]

    @classmethod
    def from_domain(cls, document):
        return cls(
            document_id=document.document_id,
            doc_type=document.doc_type.value,
            status=document.status.value,
            from_warehouse_id=document.from_warehouse_id,
            to_warehouse_id=document.to_warehouse_id,
            items=[
                DocumentProductItem(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
                for item in document.items
            ],
            created_by=document.created_by,
            approved_by=document.approved_by,
            date=document.date,
            note=document.note,
        )


# Report models
class InventoryReportItem(BaseModel):
    product_id: int
    quantity: int
    product_name: Optional[str]
    unit_value: Optional[float]


class WarehouseInventoryReport(BaseModel):
    warehouse_id: int
    warehouse_location: str
    items: List[InventoryReportItem]
    low_stock_items: List[InventoryReportItem]
    generated_at: datetime


class TotalInventoryReport(BaseModel):
    product_totals: List[InventoryReportItem]
    generated_at: datetime


class InventoryReportResponse(BaseModel):
    @classmethod
    def from_domain(cls, report):
        if hasattr(report, "warehouse_id"):
            # WarehouseInventoryReport
            return {
                "type": "warehouse_inventory",
                "warehouse_id": report.warehouse_id,
                "warehouse_location": report.warehouse_location,
                "items": [
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "product_name": item.product_name,
                        "unit_value": item.unit_value,
                    }
                    for item in report.items
                ],
                "low_stock_items": [
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "product_name": item.product_name,
                        "unit_value": item.unit_value,
                    }
                    for item in report.low_stock_items
                ],
                "generated_at": report.generated_at,
            }
        else:
            # TotalInventoryReport
            return {
                "type": "total_inventory",
                "product_totals": [
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "product_name": item.product_name,
                        "unit_value": item.unit_value,
                    }
                    for item in report.product_totals
                ],
                "generated_at": report.generated_at,
            }
