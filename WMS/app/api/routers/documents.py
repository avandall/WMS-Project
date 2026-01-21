"""
Documents API router.
Provides endpoints for document management operations.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from ..dependencies import get_document_service
from ..schemas.product import DocumentCreate, DocumentResponse, DocumentPost
from ..security import validate_id_parameter, validate_pagination_params
from app.services.document_service import DocumentService
from app.models.document_domain import DocumentType

router = APIRouter()


@router.post("/import", response_model=DocumentResponse)
async def create_import_document(
    doc: DocumentCreate, service: DocumentService = Depends(get_document_service)
):
    """Create an import document."""
    # Convert DocumentProductItem objects to dictionaries for the service
    items_dict = [item.model_dump() for item in doc.items]
    document = service.create_import_document(
        to_warehouse_id=doc.warehouse_id,
        items=items_dict,
        created_by=doc.created_by,
        note=doc.note,
    )
    return DocumentResponse.from_domain(document)


@router.post("/export", response_model=DocumentResponse)
async def create_export_document(
    doc: DocumentCreate, service: DocumentService = Depends(get_document_service)
):
    """Create an export document."""
    # Convert DocumentProductItem objects to dictionaries for the service
    items_dict = [item.model_dump() for item in doc.items]
    document = service.create_export_document(
        from_warehouse_id=doc.warehouse_id,
        items=items_dict,
        created_by=doc.created_by,
        note=doc.note,
    )
    return DocumentResponse.from_domain(document)


@router.post("/transfer", response_model=DocumentResponse)
async def create_transfer_document(
    doc: DocumentCreate, service: DocumentService = Depends(get_document_service)
):
    """Create a transfer document."""
    # Convert DocumentProductItem objects to dictionaries for the service
    items_dict = [item.model_dump() for item in doc.items]
    document = service.create_transfer_document(
        from_warehouse_id=doc.from_warehouse_id,
        to_warehouse_id=doc.to_warehouse_id,
        items=items_dict,
        created_by=doc.created_by,
        note=doc.note,
    )
    return DocumentResponse.from_domain(document)


@router.post("/{document_id}/post")
async def post_document(
    document_id: int,
    post_data: DocumentPost,
    service: DocumentService = Depends(get_document_service),
):
    """Post a document (execute the warehouse operations)."""
    validate_id_parameter(document_id, "Document")
    service.post_document(document_id, post_data.approved_by)
    return {"message": f"Document {document_id} posted successfully"}


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int, service: DocumentService = Depends(get_document_service)
):
    """Get document details."""
    validate_id_parameter(document_id, "Document")
    document = service.get_document(document_id)
    return DocumentResponse.from_domain(document)


@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    doc_type: Optional[str] = None,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    service: DocumentService = Depends(get_document_service),
):
    """Get all documents with pagination, optionally filtered by type."""
    validate_pagination_params(page, page_size)
    
    all_docs = service.document_repo.get_all()
    
    if doc_type:
        doc_type_enum = DocumentType(doc_type.upper())
        filtered_docs = [doc for doc in all_docs if doc.doc_type == doc_type_enum]
    else:
        filtered_docs = all_docs
    
    # Apply pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_docs = filtered_docs[start_idx:end_idx]
    
    return [DocumentResponse.from_domain(doc) for doc in paginated_docs]
