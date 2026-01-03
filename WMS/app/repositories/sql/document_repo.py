from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.exceptions.business_exceptions import DocumentNotFoundError
from app.models.document_domain import (
    Document,
    DocumentProduct,
    DocumentStatus,
    DocumentType,
)
from app.utils.infrastructure.id_generator import IDGenerator
from ..interfaces.interfaces import IDocumentRepo
from .models import DocumentItemModel, DocumentModel


class DocumentRepo(IDocumentRepo):
    """PostgreSQL-backed repository for documents and their items."""

    def __init__(self, session: Session):
        self.session = session
        self._sync_id_generator()

    def _sync_id_generator(self) -> None:
        max_id = self.session.execute(
            select(func.max(DocumentModel.document_id))
        ).scalar()
        start_id = (max_id or 0) + 1
        IDGenerator.reset_generator("document", start_id)

    def save(self, document: Document) -> None:
        model = self.session.get(DocumentModel, document.document_id)
        if not model:
            model = DocumentModel(
                document_id=document.document_id,
                doc_type=document.doc_type.value,
                status=document.status.value,
                from_warehouse_id=document.from_warehouse_id,
                to_warehouse_id=document.to_warehouse_id,
                created_by=document.created_by,
                approved_by=document.approved_by,
                note=document.note,
                created_at=document.date,
                posted_at=document.posted_at,
                cancelled_at=document.cancelled_at,
                cancellation_reason=document.cancellation_reason,
            )
            self.session.add(model)
        else:
            model.doc_type = document.doc_type.value
            model.status = document.status.value
            model.from_warehouse_id = document.from_warehouse_id
            model.to_warehouse_id = document.to_warehouse_id
            model.created_by = document.created_by
            model.approved_by = document.approved_by
            model.note = document.note
            model.created_at = document.date
            model.posted_at = document.posted_at
            model.cancelled_at = document.cancelled_at
            model.cancellation_reason = document.cancellation_reason

            # Clear existing items before re-adding
            model.items.clear()

        # Replace items with current state
        for item in document.items:
            model.items.append(
                DocumentItemModel(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
            )

        self.session.commit()

    def get(self, document_id: int) -> Optional[Document]:
        model = self.session.get(DocumentModel, document_id)
        return self._to_domain(model) if model else None

    def get_all(self) -> List[Document]:
        rows = self.session.execute(select(DocumentModel)).scalars().all()
        return [self._to_domain(row) for row in rows]

    def update_status(self, document_id: int, new_status: DocumentStatus) -> None:
        model = self.session.get(DocumentModel, document_id)
        if not model:
            raise DocumentNotFoundError(f"Document {document_id} not found")
        model.status = new_status.value
        self.session.commit()

    def delete(self, document_id: int) -> None:
        model = self.session.get(DocumentModel, document_id)
        if not model:
            raise DocumentNotFoundError(f"Document {document_id} not found")
        self.session.delete(model)
        self.session.commit()

    def get_document(self, document_id: int) -> Document:
        doc = self.get(document_id)
        if not doc:
            raise DocumentNotFoundError(f"Document {document_id} not found")
        return doc

    @staticmethod
    def _to_domain(model: DocumentModel) -> Document:
        items = [
            DocumentProduct(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in model.items
        ]
        document = Document(
            document_id=model.document_id,
            doc_type=DocumentType(model.doc_type),
            from_warehouse_id=model.from_warehouse_id,
            to_warehouse_id=model.to_warehouse_id,
            items=items,
            created_by=model.created_by,
            note=model.note,
        )
        document.status = DocumentStatus(model.status)
        document.date = model.created_at
        document.posted_at = model.posted_at
        document.cancelled_at = model.cancelled_at
        document.cancellation_reason = model.cancellation_reason
        document.approved_by = model.approved_by
        return document
