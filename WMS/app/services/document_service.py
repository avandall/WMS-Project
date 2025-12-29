from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.document_domain import Document, DocumentType, DocumentStatus, DocumentProduct
from app.exceptions.business_exceptions import (
    DocumentNotFoundError, InvalidDocumentStatusError, ValidationError,
    InsufficientStockError, EntityNotFoundError
)
from app.repositories.interfaces.interfaces import IDocumentRepo, IWarehouseRepo, IProductRepo, IInventoryRepo
from app.utils.infrastructure import document_id_generator

class DocumentService:
    """
    Orchestrates document lifecycle management with proper transaction handling.
    Handles the complete workflow from creation to posting/cancellation.
    """

    def __init__(self, document_repo: IDocumentRepo, warehouse_repo: IWarehouseRepo,
                 product_repo: IProductRepo, inventory_repo: IInventoryRepo):
        self.document_repo = document_repo
        self.warehouse_repo = warehouse_repo
        self.product_repo = product_repo
        self.inventory_repo = inventory_repo
        self._doc_id_generator = document_id_generator()

    def create_import_document(self, to_warehouse_id: int, items: List[Dict[str, Any]],
                             created_by: str, note: Optional[str] = None) -> Document:
        """
        Create an import document with full validation and business rules.

        Orchestrates:
        1. Validate warehouse exists
        2. Validate all products exist
        3. Convert items to domain objects
        4. Create document in DRAFT status
        """
        # Validate warehouse exists
        warehouse = self.warehouse_repo.get(to_warehouse_id)
        if not warehouse:
            raise EntityNotFoundError(f"Warehouse {to_warehouse_id} not found")

        # Validate and convert items
        document_items = self._validate_and_convert_items(items)

        # Generate document
        document_id = self._doc_id_generator()
        document = Document(
            document_id=document_id,
            doc_type=DocumentType.IMPORT,
            to_warehouse_id=to_warehouse_id,
            items=document_items,
            created_by=created_by,
            note=note
        )

        self.document_repo.save(document)
        return document

    def create_export_document(self, from_warehouse_id: int, items: List[Dict[str, Any]],
                             created_by: str, note: Optional[str] = None) -> Document:
        """
        Create an export document with inventory validation.

        Orchestrates:
        1. Validate warehouse exists
        2. Validate all products exist in warehouse with sufficient quantity
        3. Convert items to domain objects
        4. Create document in DRAFT status
        """
        # Validate warehouse exists
        warehouse = self.warehouse_repo.get(from_warehouse_id)
        if not warehouse:
            raise EntityNotFoundError(f"Warehouse {from_warehouse_id} not found")

        # Validate and convert items (allow insufficient stock for planning)
        document_items = self._validate_and_convert_items(items)

        # Generate document
        document_id = self._doc_id_generator()
        document = Document(
            document_id=document_id,
            doc_type=DocumentType.EXPORT,
            from_warehouse_id=from_warehouse_id,
            items=document_items,
            created_by=created_by,
            note=note
        )

        self.document_repo.save(document)
        return document

    def create_transfer_document(self, from_warehouse_id: int, to_warehouse_id: int,
                               items: List[Dict[str, Any]], created_by: str,
                               note: Optional[str] = None) -> Document:
        """
        Create a transfer document with comprehensive validation.

        Orchestrates:
        1. Validate both warehouses exist
        2. Validate all products exist in source warehouse with sufficient quantity
        3. Convert items to domain objects
        4. Create document in DRAFT status
        """
        if from_warehouse_id == to_warehouse_id:
            raise ValidationError("Cannot transfer to the same warehouse")

        # Validate warehouses exist
        from_warehouse = self.warehouse_repo.get(from_warehouse_id)
        to_warehouse = self.warehouse_repo.get(to_warehouse_id)
        if not from_warehouse:
            raise EntityNotFoundError(f"Source warehouse {from_warehouse_id} not found")
        if not to_warehouse:
            raise EntityNotFoundError(f"Destination warehouse {to_warehouse_id} not found")

        # Validate and convert items with warehouse availability
        document_items = self._validate_and_convert_items_with_warehouse_stock(items, from_warehouse_id)

        # Generate document
        document_id = self._doc_id_generator()
        document = Document(
            document_id=document_id,
            doc_type=DocumentType.TRANSFER,
            from_warehouse_id=from_warehouse_id,
            to_warehouse_id=to_warehouse_id,
            items=document_items,
            created_by=created_by,
            note=note
        )

        self.document_repo.save(document)
        return document

    def post_document(self, document_id: int, approved_by: str) -> Document:
        """
        Post a document with transactional execution of warehouse operations.

        Orchestrates:
        1. Validate document exists and is in DRAFT status
        2. Execute warehouse operations based on document type (transactional)
        3. Update document status to POSTED
        4. Return updated document
        """
        document = self._get_document_for_processing(document_id)

        try:
            # Execute operations based on document type
            if document.doc_type == DocumentType.IMPORT:
                self._execute_import_operations(document)
            elif document.doc_type == DocumentType.EXPORT:
                self._execute_export_operations(document)
            elif document.doc_type == DocumentType.TRANSFER:
                self._execute_transfer_operations(document)

            # Update document status
            document.status = DocumentStatus.POSTED
            document.approved_by = approved_by
            document.posted_at = datetime.now()

            self.document_repo.save(document)
            return document

        except Exception as e:
            # In a real system, you would rollback any partial operations here
            raise ValidationError(f"Failed to post document {document_id}: {str(e)}")

    def cancel_document(self, document_id: int, cancelled_by: str, reason: Optional[str] = None) -> Document:
        """
        Cancel a document with validation.

        Orchestrates:
        1. Validate document exists and can be cancelled
        2. Update document status to CANCELLED
        3. Record cancellation details
        """
        document = self.document_repo.get(document_id)
        if not document:
            raise DocumentNotFoundError(f"Document {document_id} not found")

        if document.status == DocumentStatus.POSTED:
            raise InvalidDocumentStatusError(f"Cannot cancel a posted document {document_id}")
        if document.status == DocumentStatus.CANCELLED:
            raise InvalidDocumentStatusError(f"Document {document_id} is already cancelled")

        document.status = DocumentStatus.CANCELLED
        document.cancelled_by = cancelled_by
        document.cancelled_at = datetime.now()
        document.cancellation_reason = reason

        self.document_repo.save(document)
        return document

    def get_document_with_details(self, document_id: int) -> Dict[str, Any]:
        """
        Get document with enriched details for display/UI purposes.
        """
        document = self.document_repo.get(document_id)
        if not document:
            raise DocumentNotFoundError(f"Document {document_id} not found")

        # Enrich with warehouse and product details
        enriched_items = []
        for item in document.items:
            product = self.product_repo.get(item.product_id)
            enriched_items.append({
                "product": product,
                "quantity": item.quantity,
                # Use pricing from the document item rather than product catalog price
                "unit_price": item.unit_price,
                "total_value": (item.unit_price * item.quantity)
            })

        warehouse_info = {}
        if document.from_warehouse_id:
            from_wh = self.warehouse_repo.get(document.from_warehouse_id)
            warehouse_info["from_warehouse"] = from_wh
        if document.to_warehouse_id:
            to_wh = self.warehouse_repo.get(document.to_warehouse_id)
            warehouse_info["to_warehouse"] = to_wh

        return {
            "document": document,
            "items": enriched_items,
            "warehouses": warehouse_info,
            "total_value": sum(item["total_value"] for item in enriched_items if item["total_value"])
        }

    def get_pending_documents(self) -> List[Document]:
        """
        Get all documents that are pending (DRAFT status).
        """
        all_docs = self.document_repo.get_all()
        return [doc for doc in all_docs if doc.status == DocumentStatus.DRAFT]

    def get_documents_by_status(self, status: DocumentStatus) -> List[Document]:
        """
        Get documents filtered by status.
        """
        all_docs = self.document_repo.get_all()
        return [doc for doc in all_docs if doc.status == status]

    def _validate_and_convert_items(self, items: List[Dict[str, Any]]) -> List[DocumentProduct]:
        """Validate items and convert to domain objects."""
        if not items:
            raise ValidationError("Document must contain at least one item")

        document_items = []
        for item_data in items:
            product_id = item_data.get("product_id")
            quantity = item_data.get("quantity")
            unit_price = item_data.get("unit_price")

            if not product_id or not quantity or unit_price is None:
                raise ValidationError("Each item must have product_id, quantity, and unit_price")

            if quantity <= 0:
                raise ValidationError("Quantity must be positive")

            if unit_price < 0:
                raise ValidationError("Unit price cannot be negative")

            # Validate product exists
            product = self.product_repo.get(product_id)
            if not product:
                raise EntityNotFoundError(f"Product {product_id} not found")

            document_items.append(DocumentProduct(
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price
            ))

        return document_items

    def _validate_and_convert_items_with_warehouse_stock(self, items: List[Dict[str, Any]],
                                                       warehouse_id: int) -> List[DocumentProduct]:
        """Validate items and check warehouse stock availability."""
        document_items = self._validate_and_convert_items(items)

        # Check warehouse stock for each item
        for item in document_items:
            warehouse_inventory = self.warehouse_repo.get_warehouse_inventory(warehouse_id)
            current_quantity = 0

            for wh_item in warehouse_inventory:
                if wh_item.product_id == item.product_id:
                    current_quantity = wh_item.quantity
                    break

            if current_quantity < item.quantity:
                product = self.product_repo.get(item.product_id)
                product_name = product.name if product else f"ID:{item.product_id}"
                raise InsufficientStockError(
                    f"Insufficient stock for {product_name}: requested {item.quantity}, "
                    f"available {current_quantity}"
                )

        return document_items

    def _get_document_for_processing(self, document_id: int) -> Document:
        """Get document and validate it can be processed."""
        document = self.document_repo.get(document_id)
        if not document:
            raise DocumentNotFoundError(f"Document {document_id} not found")
        if document.status != DocumentStatus.DRAFT:
            raise InvalidDocumentStatusError(f"Document {document_id} is not in DRAFT status")
        return document

    def _execute_import_operations(self, document: Document) -> None:
        """Execute warehouse operations for import document.
        Ensure destination warehouse exists before any changes and avoid partial updates."""
        # Validate destination warehouse still exists at posting time
        to_warehouse = self.warehouse_repo.get(document.to_warehouse_id)
        if not to_warehouse:
            raise EntityNotFoundError(f"Warehouse {document.to_warehouse_id} not found")

        for item in document.items:
            # Add to warehouse first; if this fails, do not alter total inventory
            self.warehouse_repo.add_product_to_warehouse(
                document.to_warehouse_id, item.product_id, item.quantity
            )

            # Then add to total inventory (import brings new stock into system)
            self.inventory_repo.add_quantity(item.product_id, item.quantity)

    def _execute_export_operations(self, document: Document) -> None:
        """Execute warehouse operations for export document.
        Validate source warehouse existence before any changes."""
        from_warehouse = self.warehouse_repo.get(document.from_warehouse_id)
        if not from_warehouse:
            raise EntityNotFoundError(f"Warehouse {document.from_warehouse_id} not found")

        for item in document.items:
            # Remove from warehouse
            self.warehouse_repo.remove_product_from_warehouse(
                document.from_warehouse_id, item.product_id, item.quantity
            )
            
            # Remove from total inventory (export removes stock from system)
            self.inventory_repo.remove_quantity(item.product_id, item.quantity)

    def _execute_transfer_operations(self, document: Document) -> None:
        """Execute warehouse operations for transfer document.
        Validate both warehouses exist before any changes."""
        from_warehouse = self.warehouse_repo.get(document.from_warehouse_id)
        to_warehouse = self.warehouse_repo.get(document.to_warehouse_id)
        if not from_warehouse:
            raise EntityNotFoundError(f"Warehouse {document.from_warehouse_id} not found")
        if not to_warehouse:
            raise EntityNotFoundError(f"Warehouse {document.to_warehouse_id} not found")

        for item in document.items:
            # Remove from source
            self.warehouse_repo.remove_product_from_warehouse(
                document.from_warehouse_id, item.product_id, item.quantity
            )
            # Add to destination
            self.warehouse_repo.add_product_to_warehouse(
                document.to_warehouse_id, item.product_id, item.quantity
            )