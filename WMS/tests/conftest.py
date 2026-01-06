"""
Pytest configuration and fixtures for WMS tests.
Sets up common fixtures for testing.
"""

import pytest
import httpx
from typing import Any

# Lazy load app to avoid DB connection during SQL tests
APP_AVAILABLE = True
app = None

def lazy_load_app():
    """Lazy load app imports to avoid DB connection during SQL tests."""
    global app, APP_AVAILABLE
    if app is not None:
        return
    try:
        from app.api import app as _app
        app = _app
    except (ImportError, ModuleNotFoundError):
        APP_AVAILABLE = False
        raise


@pytest.fixture(autouse=True, scope="function")
def reset_db_for_integration_tests(request):
    """
    Auto-cleanup fixture for integration tests.
    Drops and recreates all tables before each integration test.
    """
    # Only apply to integration tests (not unit or SQL tests)
    if "integration" not in str(request.fspath) and "test_db_isolation" not in str(request.fspath):
        yield
        return
    
    # Import only when needed for integration tests
    from app.core.settings import settings
    from sqlalchemy import create_engine
    from app.repositories.sql.models import Base
    
    # Create engine for integration test cleanup
    engine = create_engine(settings.database_url)
    
    # Drop and recreate all tables before each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Cleanup
    engine.dispose()


@pytest.fixture
def client() -> Any:
    """FastAPI test client for integration tests."""
    from starlette.testclient import TestClient
    
    lazy_load_app()
    if not APP_AVAILABLE or app is None:
        pytest.skip("App dependencies not available")
    
    return TestClient(app)


@pytest.fixture
def sample_product():
    """Fixture for a sample product."""
    from app.models.product_domain import Product
    return Product(
        product_id=1,
        name="Test Laptop",
        description="High-performance laptop",
        price=999.99,
    )


@pytest.fixture
def sample_warehouse():
    """Fixture for a sample warehouse."""
    from app.models.inventory_domain import InventoryItem
    from app.models.warehouse_domain import Warehouse
    return Warehouse(
        warehouse_id=1,
        location="Main Warehouse",
        inventory=[
            InventoryItem(product_id=1, quantity=10),
            InventoryItem(product_id=2, quantity=5),
        ],
    )


@pytest.fixture
def sample_document():
    """Fixture for a sample inventory document."""
    from app.models.document_domain import Document, DocumentProduct, DocumentType
    items = [
        DocumentProduct(product_id=1, quantity=10, unit_price=99.99),
        DocumentProduct(product_id=2, quantity=5, unit_price=49.99),
    ]
    return Document(
        document_id=1,
        doc_type=DocumentType.IMPORT,
        to_warehouse_id=1,
        items=items,
        created_by="Test User",
    )
