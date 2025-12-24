from typing import List, Optional
from ..domain.document_domain import Document, DocumentType, DocumentStatus, DocumentProduct
from ..module.custom_exceptions import DocumentNotFoundError

class DocumentRepo:
    def __init__(self):
        self.documents = {}  # document_id: Document
    
    def save(self, document: Document) -> None:
        self.documents[document.document_id] = document
    
    def get(self, document_id: int) -> Optional[Document]:
        return self.documents.get(document_id)
    
    def get_all(self) -> List[Document]:
        return list(self.documents.values())
    
    def update_status(self, document_id: int, new_status: DocumentStatus) -> None:
        if document_id in self.documents:
            self.documents[document_id].status = new_status
        else:
            raise DocumentNotFoundError(f"Document {document_id} not found")
    
    def delete(self, document_id: int) -> None:
        if document_id in self.documents:
            del self.documents[document_id]
        else:
            raise DocumentNotFoundError(f"Document {document_id} not found")

    def create_import_document(self, document_id: int, to_warehouse_id: int, items: List[DocumentProduct], created_by: str, note: str = None) -> Document:
        doc = Document(
            document_id=document_id,
            doc_type=DocumentType.IMPORT,
            to_warehouse_id=to_warehouse_id,
            items=items,
            created_by=created_by,
            note=note
        )
        self.save(doc)
        return doc

    def create_export_document(self, document_id: int, from_warehouse_id: int, items: List[DocumentProduct], created_by: str, note: str = None) -> Document:
        doc = Document(
            document_id=document_id,
            doc_type=DocumentType.EXPORT,
            from_warehouse_id=from_warehouse_id,
            items=items,
            created_by=created_by,
            note=note
        )
        self.save(doc)
        return doc

    def create_transfer_document(self, document_id: int, from_warehouse_id: int, to_warehouse_id: int, items: List[DocumentProduct], created_by: str, note: str = None) -> Document:
        doc = Document(
            document_id=document_id,
            doc_type=DocumentType.TRANSFER,
            from_warehouse_id=from_warehouse_id,
            to_warehouse_id=to_warehouse_id,
            items=items,
            created_by=created_by,
            note=note
        )
        self.save(doc)
        return doc

    def get_document(self, document_id: int) -> Document:
        doc = self.get(document_id)
        if not doc:
            raise DocumentNotFoundError(f"Document {document_id} not found")
        return doc