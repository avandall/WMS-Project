"""
Documents API router.
Provides endpoints for document management operations.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from ..dependencies import get_document_service
from ..schemas.product import DocumentCreate, DocumentResponse, DocumentPost
from app.services.document_service import DocumentService

router = APIRouter()

@router.post("/import", response_model=DocumentResponse)
async def create_import_document(
    doc: DocumentCreate,
    service: DocumentService = Depends(get_document_service)
):
    """Create an import document."""
    try:
        # Convert DocumentProductItem objects to dictionaries for the service
        items_dict = [item.model_dump() for item in doc.items]
        document = service.create_import_document(
            to_warehouse_id=doc.warehouse_id,
            items=items_dict,
            created_by=doc.created_by,
            note=doc.note
        )
        return DocumentResponse.from_domain(document)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/export", response_model=DocumentResponse)
async def create_export_document(
    doc: DocumentCreate,
    service: DocumentService = Depends(get_document_service)
):
    """Create an export document."""
    try:
        # Convert DocumentProductItem objects to dictionaries for the service
        items_dict = [item.dict() for item in doc.items]
        document = service.create_export_document(
            from_warehouse_id=doc.warehouse_id,
            items=items_dict,
            created_by=doc.created_by,
            note=doc.note
        )
        return DocumentResponse.from_domain(document)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/transfer", response_model=DocumentResponse)
async def create_transfer_document(
    doc: DocumentCreate,
    service: DocumentService = Depends(get_document_service)
):
    """Create a transfer document."""
    try:
        # Convert DocumentProductItem objects to dictionaries for the service
        items_dict = [item.dict() for item in doc.items]
        document = service.create_transfer_document(
            from_warehouse_id=doc.from_warehouse_id,
            to_warehouse_id=doc.to_warehouse_id,
            items=items_dict,
            created_by=doc.created_by,
            note=doc.note
        )
        return DocumentResponse.from_domain(document)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{document_id}/post")
async def post_document(
    document_id: int,
    post_data: DocumentPost,
    service: DocumentService = Depends(get_document_service)
):
    """Post a document (execute the warehouse operations)."""
    try:
        service.post_document(document_id, post_data.approved_by)
        return {"message": f"Document {document_id} posted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    service: DocumentService = Depends(get_document_service)
):
    """Get document details."""
    try:
        document = service.get_document(document_id)
        return DocumentResponse.from_domain(document)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    doc_type: Optional[str] = None,
    service: DocumentService = Depends(get_document_service)
):
    """Get all documents, optionally filtered by type."""
    try:
        doc_type_enum = None
        if doc_type:
            doc_type_enum = DocumentType(doc_type.upper())
        documents = service.get_documents_by_status(doc_type_enum)
        return [DocumentResponse.from_domain(doc) for doc in documents]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))