"""
Pytest configuration and fixtures for PMKT tests.
"""
import pytest
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PMKT.repo.product_repo import ProductRepo
from PMKT.repo.warehouse_repo import WarehouseRepo
from PMKT.repo.document_repo import DocumentRepo
from PMKT.services.product_service import ProductService
from PMKT.services.inventory_service import InventoryService
from PMKT.domain.product_domain import Product
from PMKT.domain.warehouse_domain import Warehouse
from PMKT.domain.document_domain import Document, DocumentProduct, DocumentType, DocumentStatus


@pytest.fixture
def product_repo():
    """Fixture for product repository."""
    return ProductRepo()


@pytest.fixture
def warehouse_repo():
    """Fixture for warehouse repository."""
    return WarehouseRepo()


@pytest.fixture
def document_repo():
    """Fixture for document repository."""
    return DocumentRepo()


@pytest.fixture
def product_service(product_repo):
    """Fixture for product service."""
    return ProductService(product_repo)


@pytest.fixture
def inventory_service():
    """Fixture for inventory service."""
    from PMKT.repo.inventory_repo import InventoryRepo
    from PMKT.services.inventory_service import InventoryService
    return InventoryService(InventoryRepo())


@pytest.fixture
def sample_product():
    """Fixture for a sample product."""
    return Product(
        product_id=1,
        name="Test Laptop",
        description="High-performance laptop",
        price=999.99
    )


@pytest.fixture
def sample_warehouse():
    """Fixture for a sample warehouse."""
    from PMKT.domain.inventory_domain import InventoryItem
    return Warehouse(
        warehouse_id=1,
        location="Main Warehouse",
        inventory=[
            InventoryItem(product_id=1, quantity=10),
            InventoryItem(product_id=2, quantity=5)
        ]
    )


@pytest.fixture
def sample_document():
    """Fixture for a sample inventory document."""
    items = [
        DocumentProduct(product_id=1, quantity=10, unit_price=99.99),
        DocumentProduct(product_id=2, quantity=5, unit_price=49.99)
    ]
    return Document(
        document_id=1,
        doc_type=DocumentType.IMPORT,
        to_warehouse_id=1,
        items=items,
        created_by="Test User"
    )