"""
Document domain logic for PMKT Warehouse Management System.
Contains business rules and validation for document operations.
"""

from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.exceptions.business_exceptions import ValidationError, BusinessRuleViolationError, EntityNotFoundError, InvalidIDError, InvalidQuantityError, InvalidDocumentStatusError
from app.core.error_constants import ErrorMessages

# Local enums to avoid dependency on models.py
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


class DocumentProduct:
    """Domain class for DocumentProduct with business logic and validation."""

    def __init__(self, product_id: int, quantity: int, unit_price: float):
        self._validate_product_id(product_id)
        self._validate_quantity(quantity)
        self._validate_unit_price(unit_price)

        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price

    @staticmethod
    def _validate_product_id(product_id: int) -> None:
        """Validate product ID."""
        if not isinstance(product_id, int) or product_id <= 0:
            raise InvalidIDError(ErrorMessages.INVALID_PRODUCT_ID)

    @staticmethod
    def _validate_quantity(quantity: int) -> None:
        """Validate quantity."""
        if not isinstance(quantity, int) or quantity <= 0:
            raise InvalidQuantityError(ErrorMessages.INVALID_QUANTITY_POSITIVE)

    @staticmethod
    def _validate_unit_price(unit_price: float) -> None:
        """Validate unit price."""
        if not isinstance(unit_price, (int, float)) or unit_price < 0:
            raise InvalidQuantityError(ErrorMessages.INVALID_UNIT_PRICE_NEGATIVE)

    def calculate_total_value(self) -> float:
        """Calculate total value for this document product."""
        return self.quantity * self.unit_price

    def __str__(self) -> str:
        return f"DocumentProduct(product_id={self.product_id}, quantity={self.quantity}, unit_price={self.unit_price})"

    def __repr__(self) -> str:
        return self.__str__()


class Document:
    """Domain class for Document with business logic and validation."""

    def __init__(self, document_id: int, doc_type: DocumentType, from_warehouse_id: Optional[int] = None,
                 to_warehouse_id: Optional[int] = None, items: Optional[List[DocumentProduct]] = None,
                 created_by: str = "", note: Optional[str] = None):
        self._validate_document_id(document_id)
        self._validate_document_type(doc_type)
        self._validate_warehouses(doc_type, from_warehouse_id, to_warehouse_id)
        self._validate_created_by(created_by)

        self.document_id = document_id
        self.doc_type = doc_type
        self.status = DocumentStatus.DRAFT
        self.date = datetime.now()
        self.from_warehouse_id = from_warehouse_id
        self.to_warehouse_id = to_warehouse_id
        self.items: List[DocumentProduct] = items or []
        self.created_by = created_by
        self.note = note
        self.approved_by: Optional[str] = None

    @staticmethod
    def _validate_document_id(document_id: int) -> None:
        """Validate document ID."""
        if not isinstance(document_id, int) or document_id <= 0:
            raise InvalidIDError(ErrorMessages.INVALID_DOCUMENT_ID)

    @staticmethod
    def _validate_document_type(doc_type) -> None:
        """Validate document type."""
        if doc_type not in [DocumentType.IMPORT, DocumentType.EXPORT, DocumentType.TRANSFER]:
            raise ValidationError(ErrorMessages.INVALID_DOCUMENT_TYPE)

    @staticmethod
    def _validate_warehouses(doc_type: DocumentType, from_warehouse_id: Optional[int], to_warehouse_id: Optional[int]) -> None:
        """Validate warehouse requirements based on document type."""
        if doc_type == DocumentType.IMPORT:
            if to_warehouse_id is None:
                raise ValidationError(ErrorMessages.IMPORT_MISSING_DESTINATION)
        elif doc_type == DocumentType.EXPORT:
            if from_warehouse_id is None:
                raise ValidationError(ErrorMessages.EXPORT_MISSING_SOURCE)
        elif doc_type == DocumentType.TRANSFER:
            if from_warehouse_id is None or to_warehouse_id is None:
                raise ValidationError(ErrorMessages.TRANSFER_MISSING_WAREHOUSES)
            if from_warehouse_id == to_warehouse_id:
                raise BusinessRuleViolationError(ErrorMessages.TRANSFER_SAME_WAREHOUSE)

    @staticmethod
    def _validate_created_by(created_by: str) -> None:
        """Validate created_by field."""
        if not created_by or not isinstance(created_by, str) or len(created_by.strip()) == 0:
            raise ValidationError(ErrorMessages.INVALID_CREATED_BY_EMPTY)

    def add_item(self, item: DocumentProduct) -> None:
        """Add an item to the document."""
        self._ensure_draft_status()
        # Check if product already exists
        for existing_item in self.items:
            if existing_item.product_id == item.product_id:
                raise BusinessRuleViolationError(f"Product {item.product_id} already exists in document")
        self.items.append(item)

    def remove_item(self, product_id: int) -> None:
        """Remove an item from the document."""
        self._ensure_draft_status()
        for i, item in enumerate(self.items):
            if item.product_id == product_id:
                self.items.pop(i)
                return
        raise EntityNotFoundError(f"Product {product_id} not found in document")

    def update_item(self, product_id: int, quantity: int, unit_price: float) -> None:
        """Update an item in the document."""
        self._ensure_draft_status()
        for item in self.items:
            if item.product_id == product_id:
                item.quantity = quantity
                item.unit_price = unit_price
                return
        raise EntityNotFoundError(f"Product {product_id} not found in document")

    def post(self, approved_by: str) -> None:
        """Post the document (change status to POSTED)."""
        if self.status != DocumentStatus.DRAFT:
            raise InvalidDocumentStatusError(f"Document {self.document_id} is not in DRAFT status")
        if not approved_by or not isinstance(approved_by, str):
            raise ValidationError("Approved by cannot be empty")
        if not self.items:
            raise BusinessRuleViolationError("Cannot post document without items")

        self.status = DocumentStatus.POSTED
        self.approved_by = approved_by

    def cancel(self) -> None:
        """Cancel the document."""
        if self.status == DocumentStatus.POSTED:
            raise InvalidDocumentStatusError(f"Cannot cancel a posted document {self.document_id}")
        self.status = DocumentStatus.CANCELLED

    def _ensure_draft_status(self) -> None:
        """Ensure document is in draft status for modifications."""
        if self.status != DocumentStatus.DRAFT:
            raise InvalidDocumentStatusError(f"Cannot modify document {self.document_id} that is not in DRAFT status")

    def calculate_total_value(self) -> float:
        """Calculate total value of all items in the document."""
        return sum(item.calculate_total_value() for item in self.items)

    def get_summary(self) -> dict:
        """Get document summary."""
        return {
            'document_id': self.document_id,
            'type': self.doc_type.value,
            'status': self.status.value,
            'date': self.date.isoformat(),
            'from_warehouse': self.from_warehouse_id,
            'to_warehouse': self.to_warehouse_id,
            'total_items': len(self.items),
            'total_quantity': sum(item.quantity for item in self.items),
            'total_value': self.calculate_total_value(),
            'created_by': self.created_by,
            'approved_by': self.approved_by
        }

    def can_be_modified(self) -> bool:
        """Check if document can be modified."""
        return self.status == DocumentStatus.DRAFT

    def __str__(self) -> str:
        return f"Document(id={self.document_id}, type={self.doc_type.value}, status={self.status.value}, items={len(self.items)})"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, Document):
            return False
        return self.document_id == other.document_id

    def __hash__(self) -> int:
        return hash(self.document_id)