"""
Command objects for the Application Layer.
Commands represent write operations in CQRS pattern.
"""

from typing import List, Optional
from dataclasses import dataclass
from app.application.dto import (
    CreateProductDTO, UpdateProductDTO, CreateWarehouseDTO,
    CreateDocumentDTO
)


# Product Commands
@dataclass(frozen=True)
class CreateProductCommand:
    """Command to create a new product."""
    product_data: CreateProductDTO


@dataclass(frozen=True)
class UpdateProductCommand:
    """Command to update an existing product."""
    product_id: int
    update_data: UpdateProductDTO


@dataclass(frozen=True)
class DeleteProductCommand:
    """Command to delete a product."""
    product_id: int


# Warehouse Commands
@dataclass(frozen=True)
class CreateWarehouseCommand:
    """Command to create a new warehouse."""
    warehouse_data: CreateWarehouseDTO


@dataclass(frozen=True)
class UpdateWarehouseCommand:
    """Command to update warehouse information."""
    warehouse_id: int
    location: str


@dataclass(frozen=True)
class DeleteWarehouseCommand:
    """Command to delete a warehouse."""
    warehouse_id: int


# Inventory Commands
@dataclass(frozen=True)
class AddInventoryCommand:
    """Command to add inventory to a warehouse."""
    warehouse_id: int
    product_id: int
    quantity: int


@dataclass(frozen=True)
class RemoveInventoryCommand:
    """Command to remove inventory from a warehouse."""
    warehouse_id: int
    product_id: int
    quantity: int


@dataclass(frozen=True)
class TransferInventoryCommand:
    """Command to transfer inventory between warehouses."""
    from_warehouse_id: int
    to_warehouse_id: int
    product_id: int
    quantity: int


# Document Commands
@dataclass(frozen=True)
class CreateDocumentCommand:
    """Command to create a new document."""
    document_data: CreateDocumentDTO


@dataclass(frozen=True)
class ProcessDocumentCommand:
    """Command to process/execute a document."""
    document_id: int
    processed_by: str


@dataclass(frozen=True)
class CancelDocumentCommand:
    """Command to cancel a document."""
    document_id: int
    cancelled_by: str
    reason: Optional[str] = None


# Command Results
@dataclass(frozen=True)
class CommandResult:
    """Result of a command execution."""
    success: bool
    message: str
    data: Optional[dict] = None


@dataclass(frozen=True)
class CreateProductResult(CommandResult):
    """Result of creating a product."""
    product_id: Optional[int] = None


@dataclass(frozen=True)
class CreateWarehouseResult(CommandResult):
    """Result of creating a warehouse."""
    warehouse_id: Optional[int] = None


@dataclass(frozen=True)
class CreateDocumentResult(CommandResult):
    """Result of creating a document."""
    document_id: Optional[int] = None