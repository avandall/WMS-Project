from typing import List, Optional
from ..domain.document_domain import Document, DocumentType, DocumentStatus, DocumentProduct
from ..module.custom_exceptions import DocumentNotFoundError, InvalidDocumentStatusError
from ..repo.document_repo import DocumentRepo
from .warehouse_service import WarehouseService
from ..utils.infrastructure import document_id_generator

class DocumentService:
    def __init__(self, repo: DocumentRepo, warehouse_service: WarehouseService):
        self.repo = repo
        self.warehouse_service = warehouse_service
        self._doc_id_generator = document_id_generator()
    
    def create_import_document(self, to_warehouse_id: int, items: List[DocumentProduct], created_by: str, note: str = None) -> Document:
        document_id = self._doc_id_generator()
        return self.repo.create_import_document(document_id, to_warehouse_id, items, created_by, note)
    
    def create_export_document(self, from_warehouse_id: int, items: List[DocumentProduct], created_by: str, note: str = None) -> Document:
        document_id = self._doc_id_generator()
        return self.repo.create_export_document(document_id, from_warehouse_id, items, created_by, note)
    
    def create_transfer_document(self, from_warehouse_id: int, to_warehouse_id: int, items: List[DocumentProduct], created_by: str, note: str = None) -> Document:
        document_id = self._doc_id_generator()
        return self.repo.create_transfer_document(document_id, from_warehouse_id, to_warehouse_id, items, created_by, note)
    
    def post_document(self, document_id: int, approved_by: str) -> None:
        doc = self.repo.get(document_id)
        if not doc:
            raise DocumentNotFoundError(f"Document {document_id} not found")
        if doc.status != DocumentStatus.DRAFT:
            raise InvalidDocumentStatusError(f"Document {document_id} is not in DRAFT status")
        
        # Perform the warehouse operations based on document type
        if doc.doc_type == DocumentType.IMPORT:
            for item in doc.items:
                self.warehouse_service.add_product_to_warehouse(doc.to_warehouse_id, item.product_id, item.quantity)
        elif doc.doc_type == DocumentType.EXPORT:
            for item in doc.items:
                self.warehouse_service.remove_product_from_warehouse(doc.from_warehouse_id, item.product_id, item.quantity)
        elif doc.doc_type == DocumentType.TRANSFER:
            for item in doc.items:
                self.warehouse_service.remove_product_from_warehouse(doc.from_warehouse_id, item.product_id, item.quantity)
                self.warehouse_service.add_product_to_warehouse(doc.to_warehouse_id, item.product_id, item.quantity)
        
        doc.status = DocumentStatus.POSTED
        doc.approved_by = approved_by
        self.repo.save(doc)
    
    def cancel_document(self, document_id: int) -> None:
        doc = self.repo.get(document_id)
        if not doc:
            raise ValueError(f"Document {document_id} not found")
        if doc.status == DocumentStatus.POSTED:
            raise InvalidDocumentStatusError(f"Cannot cancel a posted document {document_id}")
        doc.status = DocumentStatus.CANCELLED
        self.repo.save(doc)
    
    def get_document(self, document_id: int) -> Document:
        return self.repo.get_document(document_id)
    
    def get_all_documents(self, doc_type: Optional[DocumentType] = None) -> List[Document]:
        all_docs = self.repo.get_all()
        if doc_type:
            return [doc for doc in all_docs if doc.doc_type == doc_type]
        return all_docs