from typing import List, Optional
from app.models.document_domain import Document, DocumentType, DocumentStatus, DocumentProduct
from app.exceptions.business_exceptions import DocumentNotFoundError
from ..interfaces.interfaces import IDocumentRepo

class DocumentRepo(IDocumentRepo):
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

    def get_document(self, document_id: int) -> Document:
        doc = self.get(document_id)
        if not doc:
            raise DocumentNotFoundError(f"Document {document_id} not found")
        return doc