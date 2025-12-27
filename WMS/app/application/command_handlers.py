"""
Command Handlers for the Application Layer.
These handle write operations and orchestrate domain logic.
"""

from typing import Protocol
from abc import ABC, abstractmethod
from app.application.commands import (
    CreateProductCommand, UpdateProductCommand, DeleteProductCommand,
    CreateWarehouseCommand, UpdateWarehouseCommand, DeleteWarehouseCommand,
    AddInventoryCommand, RemoveInventoryCommand, TransferInventoryCommand,
    CreateDocumentCommand, ProcessDocumentCommand, CancelDocumentCommand,
    CommandResult, CreateProductResult, CreateWarehouseResult, CreateDocumentResult
)
from app.services.product_service import ProductService
from app.services.warehouse_service import WarehouseService
from app.services.inventory_service import InventoryService
from app.services.document_service import DocumentService


class CommandHandler(Protocol):
    """Protocol for command handlers."""

    def handle(self, command) -> CommandResult:
        """Handle the command and return a result."""
        ...


# Product Command Handlers
class CreateProductHandler:
    """Handler for creating products."""

    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def handle(self, command: CreateProductCommand) -> CreateProductResult:
        try:
            product = self.product_service.create_product(
                product_id=command.product_data.product_id,
                name=command.product_data.name,
                price=command.product_data.price,
                description=command.product_data.description
            )
            return CreateProductResult(
                success=True,
                message="Product created successfully",
                product_id=product.product_id
            )
        except Exception as e:
            return CreateProductResult(
                success=False,
                message=f"Failed to create product: {str(e)}"
            )


class UpdateProductHandler:
    """Handler for updating products."""

    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def handle(self, command: UpdateProductCommand) -> CommandResult:
        try:
            self.product_service.update_product(
                product_id=command.product_id,
                **command.update_data.model_dump(exclude_unset=True)
            )
            return CommandResult(
                success=True,
                message="Product updated successfully"
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to update product: {str(e)}"
            )


class DeleteProductHandler:
    """Handler for deleting products."""

    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def handle(self, command: DeleteProductCommand) -> CommandResult:
        try:
            self.product_service.delete_product(command.product_id)
            return CommandResult(
                success=True,
                message="Product deleted successfully"
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to delete product: {str(e)}"
            )


# Warehouse Command Handlers
class CreateWarehouseHandler:
    """Handler for creating warehouses."""

    def __init__(self, warehouse_service: WarehouseService):
        self.warehouse_service = warehouse_service

    def handle(self, command: CreateWarehouseCommand) -> CreateWarehouseResult:
        try:
            warehouse = self.warehouse_service.create_warehouse(
                location=command.warehouse_data.location
            )
            return CreateWarehouseResult(
                success=True,
                message="Warehouse created successfully",
                warehouse_id=warehouse.warehouse_id
            )
        except Exception as e:
            return CreateWarehouseResult(
                success=False,
                message=f"Failed to create warehouse: {str(e)}"
            )


class UpdateWarehouseHandler:
    """Handler for updating warehouses."""

    def __init__(self, warehouse_service: WarehouseService):
        self.warehouse_service = warehouse_service

    def handle(self, command: UpdateWarehouseCommand) -> CommandResult:
        try:
            self.warehouse_service.update_warehouse(
                warehouse_id=command.warehouse_id,
                location=command.location
            )
            return CommandResult(
                success=True,
                message="Warehouse updated successfully"
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to update warehouse: {str(e)}"
            )


class DeleteWarehouseHandler:
    """Handler for deleting warehouses."""

    def __init__(self, warehouse_service: WarehouseService):
        self.warehouse_service = warehouse_service

    def handle(self, command: DeleteWarehouseCommand) -> CommandResult:
        try:
            self.warehouse_service.delete_warehouse(command.warehouse_id)
            return CommandResult(
                success=True,
                message="Warehouse deleted successfully"
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to delete warehouse: {str(e)}"
            )


# Inventory Command Handlers
class AddInventoryHandler:
    """Handler for adding inventory."""

    def __init__(self, inventory_service: InventoryService):
        self.inventory_service = inventory_service

    def handle(self, command: AddInventoryCommand) -> CommandResult:
        try:
            self.inventory_service.add_inventory(
                warehouse_id=command.warehouse_id,
                product_id=command.product_id,
                quantity=command.quantity
            )
            return CommandResult(
                success=True,
                message="Inventory added successfully"
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to add inventory: {str(e)}"
            )


class RemoveInventoryHandler:
    """Handler for removing inventory."""

    def __init__(self, inventory_service: InventoryService):
        self.inventory_service = inventory_service

    def handle(self, command: RemoveInventoryCommand) -> CommandResult:
        try:
            self.inventory_service.remove_inventory(
                warehouse_id=command.warehouse_id,
                product_id=command.product_id,
                quantity=command.quantity
            )
            return CommandResult(
                success=True,
                message="Inventory removed successfully"
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to remove inventory: {str(e)}"
            )


class TransferInventoryHandler:
    """Handler for transferring inventory."""

    def __init__(self, inventory_service: InventoryService):
        self.inventory_service = inventory_service

    def handle(self, command: TransferInventoryCommand) -> CommandResult:
        try:
            self.inventory_service.transfer_inventory(
                from_warehouse_id=command.from_warehouse_id,
                to_warehouse_id=command.to_warehouse_id,
                product_id=command.product_id,
                quantity=command.quantity
            )
            return CommandResult(
                success=True,
                message="Inventory transferred successfully"
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to transfer inventory: {str(e)}"
            )


# Document Command Handlers
class CreateDocumentHandler:
    """Handler for creating documents."""

    def __init__(self, document_service: DocumentService):
        self.document_service = document_service

    def handle(self, command: CreateDocumentCommand) -> CreateDocumentResult:
        try:
            document = self.document_service.create_document(
                doc_type=command.document_data.doc_type,
                from_warehouse_id=command.document_data.from_warehouse_id,
                to_warehouse_id=command.document_data.to_warehouse_id,
                items=command.document_data.items,
                created_by=command.document_data.created_by,
                note=getattr(command.document_data, 'note', None)
            )
            return CreateDocumentResult(
                success=True,
                message="Document created successfully",
                document_id=document.document_id
            )
        except Exception as e:
            return CreateDocumentResult(
                success=False,
                message=f"Failed to create document: {str(e)}"
            )


class ProcessDocumentHandler:
    """Handler for processing documents."""

    def __init__(self, document_service: DocumentService):
        self.document_service = document_service

    def handle(self, command: ProcessDocumentCommand) -> CommandResult:
        try:
            self.document_service.process_document(
                document_id=command.document_id,
                processed_by=command.processed_by
            )
            return CommandResult(
                success=True,
                message="Document processed successfully"
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to process document: {str(e)}"
            )


class CancelDocumentHandler:
    """Handler for canceling documents."""

    def __init__(self, document_service: DocumentService):
        self.document_service = document_service

    def handle(self, command: CancelDocumentCommand) -> CommandResult:
        try:
            self.document_service.cancel_document(
                document_id=command.document_id,
                cancelled_by=command.cancelled_by,
                reason=command.reason
            )
            return CommandResult(
                success=True,
                message="Document cancelled successfully"
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to cancel document: {str(e)}"
            )