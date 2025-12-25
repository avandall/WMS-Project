"""
Unit tests for DocumentRepo.
"""

import pytest
from datetime import datetime
from PMKT.repo.document_repo import DocumentRepo
from PMKT.domain.document_domain import Document, DocumentType, DocumentStatus, DocumentProduct
from PMKT.module.custom_exceptions import DocumentNotFoundError


class TestDocumentRepo:
    """Test cases for DocumentRepo."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repo = DocumentRepo()

    def test_save_and_get_document(self):
        """Test saving and retrieving a document."""
        doc = Document(
            document_id=1,
            doc_type=DocumentType.IMPORT,
            to_warehouse_id=1,
            created_by="test_user"
        )

        self.repo.save(doc)
        retrieved = self.repo.get(1)

        assert retrieved is not None
        assert retrieved.document_id == 1
        assert retrieved.doc_type == DocumentType.IMPORT
        assert retrieved.to_warehouse_id == 1
        assert retrieved.created_by == "test_user"

    def test_get_nonexistent_document(self):
        """Test getting a document that doesn't exist."""
        result = self.repo.get(999)
        assert result is None

    def test_get_all_documents(self):
        """Test getting all documents."""
        doc1 = Document(document_id=1, doc_type=DocumentType.IMPORT, to_warehouse_id=1, created_by="user1")
        doc2 = Document(document_id=2, doc_type=DocumentType.EXPORT, from_warehouse_id=1, created_by="user2")

        self.repo.save(doc1)
        self.repo.save(doc2)

        all_docs = self.repo.get_all()
        assert len(all_docs) == 2

        doc_ids = [doc.document_id for doc in all_docs]
        assert 1 in doc_ids
        assert 2 in doc_ids

    def test_get_all_empty_repo(self):
        """Test getting all documents when repo is empty."""
        all_docs = self.repo.get_all()
        assert all_docs == []

    def test_update_status_existing_document(self):
        """Test updating status of existing document."""
        doc = Document(document_id=1, doc_type=DocumentType.IMPORT, to_warehouse_id=1, created_by="user")
        self.repo.save(doc)

        self.repo.update_status(1, DocumentStatus.POSTED)

        retrieved = self.repo.get(1)
        assert retrieved.status == DocumentStatus.POSTED

    def test_update_status_nonexistent_document(self):
        """Test updating status of nonexistent document raises DocumentNotFoundError."""
        with pytest.raises(DocumentNotFoundError, match="Document 999 not found"):
            self.repo.update_status(999, DocumentStatus.POSTED)

    def test_delete_existing_document(self):
        """Test deleting an existing document."""
        doc = Document(document_id=1, doc_type=DocumentType.IMPORT, to_warehouse_id=1, created_by="user")
        self.repo.save(doc)

        self.repo.delete(1)
        assert self.repo.get(1) is None

    def test_delete_nonexistent_document(self):
        """Test deleting a nonexistent document raises DocumentNotFoundError."""
        with pytest.raises(DocumentNotFoundError, match="Document 999 not found"):
            self.repo.delete(999)

    def test_create_import_document(self):
        """Test creating an import document."""
        items = [
            DocumentProduct(product_id=1, quantity=10, unit_price=5.0),
            DocumentProduct(product_id=2, quantity=5, unit_price=10.0)
        ]

        doc = self.repo.create_import_document(
            document_id=1,
            to_warehouse_id=100,
            items=items,
            created_by="test_user",
            note="Test import"
        )

        assert doc.document_id == 1
        assert doc.doc_type == DocumentType.IMPORT
        assert doc.to_warehouse_id == 100
        assert doc.from_warehouse_id is None
        assert doc.created_by == "test_user"
        assert doc.note == "Test import"
        assert len(doc.items) == 2
        assert doc.status == DocumentStatus.DRAFT

        # Verify it's saved
        retrieved = self.repo.get(1)
        assert retrieved is not None
        assert retrieved.doc_type == DocumentType.IMPORT

    def test_create_export_document(self):
        """Test creating an export document."""
        items = [DocumentProduct(product_id=1, quantity=5, unit_price=8.0)]

        doc = self.repo.create_export_document(
            document_id=2,
            from_warehouse_id=200,
            items=items,
            created_by="test_user"
        )

        assert doc.document_id == 2
        assert doc.doc_type == DocumentType.EXPORT
        assert doc.from_warehouse_id == 200
        assert doc.to_warehouse_id is None
        assert doc.created_by == "test_user"
        assert doc.note is None
        assert len(doc.items) == 1

    def test_create_transfer_document(self):
        """Test creating a transfer document."""
        items = [DocumentProduct(product_id=1, quantity=3, unit_price=12.0)]

        doc = self.repo.create_transfer_document(
            document_id=3,
            from_warehouse_id=200,
            to_warehouse_id=300,
            items=items,
            created_by="test_user",
            note="Warehouse transfer"
        )

        assert doc.document_id == 3
        assert doc.doc_type == DocumentType.TRANSFER
        assert doc.from_warehouse_id == 200
        assert doc.to_warehouse_id == 300
        assert doc.created_by == "test_user"
        assert doc.note == "Warehouse transfer"
        assert len(doc.items) == 1

    def test_get_document_existing(self):
        """Test getting document details for existing document."""
        doc = Document(document_id=1, doc_type=DocumentType.IMPORT, to_warehouse_id=1, created_by="user")
        self.repo.save(doc)

        retrieved = self.repo.get_document(1)
        assert retrieved.document_id == 1
        assert retrieved.doc_type == DocumentType.IMPORT

    def test_get_document_nonexistent(self):
        """Test getting document details for nonexistent document raises DocumentNotFoundError."""
        with pytest.raises(DocumentNotFoundError, match="Document 999 not found"):
            self.repo.get_document(999)

    def test_document_status_initialization(self):
        """Test that created documents have DRAFT status."""
        doc = self.repo.create_import_document(
            document_id=1,
            to_warehouse_id=1,
            items=[],
            created_by="user"
        )

        assert doc.status == DocumentStatus.DRAFT

    def test_multiple_documents(self):
        """Test handling multiple documents."""
        # Create different types of documents
        import_doc = self.repo.create_import_document(1, 1, [], "user1")
        export_doc = self.repo.create_export_document(2, 1, [], "user2")
        transfer_doc = self.repo.create_transfer_document(3, 1, 2, [], "user3")

        assert len(self.repo.get_all()) == 3

        # Update status of one
        self.repo.update_status(1, DocumentStatus.POSTED)
        assert self.repo.get(1).status == DocumentStatus.POSTED
        assert self.repo.get(2).status == DocumentStatus.DRAFT
        assert self.repo.get(3).status == DocumentStatus.DRAFT

        # Delete one
        self.repo.delete(2)
        assert len(self.repo.get_all()) == 2
        assert self.repo.get(2) is None
        assert self.repo.get(1) is not None
        assert self.repo.get(3) is not None

    def test_document_with_items(self):
        """Test document creation with items."""
        items = [
            DocumentProduct(product_id=1, quantity=10, unit_price=5.0),
            DocumentProduct(product_id=2, quantity=20, unit_price=8.0),
        ]

        doc = self.repo.create_import_document(1, 1, items, "user")

        assert len(doc.items) == 2
        assert doc.items[0].product_id == 1
        assert doc.items[0].quantity == 10
        assert doc.items[0].unit_price == 5.0
        assert doc.items[1].product_id == 2
        assert doc.items[1].quantity == 20
        assert doc.items[1].unit_price == 8.0

    def test_empty_document_creation(self):
        """Test creating documents with empty items list."""
        doc = self.repo.create_import_document(1, 1, [], "user")

        assert len(doc.items) == 0
        assert doc.status == DocumentStatus.DRAFT