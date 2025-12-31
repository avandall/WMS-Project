"""
Pytest configuration and fixtures for PMKT tests.
Sets up common fixtures and resets in-memory repositories between tests.
"""

import pytest
import httpx
import asyncio

from app.api import app
from app.api import dependencies
from app.repositories.sql.product_repo import ProductRepo
from app.repositories.sql.warehouse_repo import WarehouseRepo
from app.repositories.sql.document_repo import DocumentRepo
from app.services.product_service import ProductService
from app.services.inventory_service import InventoryService
from app.models.product_domain import Product
from app.models.warehouse_domain import Warehouse
from app.models.document_domain import Document, DocumentProduct, DocumentType


class SyncASGITransport(httpx.ASGITransport):
    """Custom sync ASGI transport that bridges async/sync."""

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        """Handle sync request by running async handler in event loop."""
        # Create a new event loop for this request
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Get the async response
            response = loop.run_until_complete(self.handle_async_request(request))
            # Convert async stream to sync
            if hasattr(response.stream, "__aiter__"):
                # Drain the async stream into a sync byte stream
                content = loop.run_until_complete(response.aread())
                response = httpx.Response(
                    status_code=response.status_code,
                    headers=response.headers,
                    content=content,
                    request=request,
                    extensions=response.extensions,
                )
            return response
        finally:
            loop.close()


@pytest.fixture(autouse=True)
def reset_state():
    """Reset singleton in-memory repos between tests to avoid cross-test bleed."""
    # Re-initialize the singletons instead of clearing internal dicts to avoid attribute errors
    dependencies._product_repo = dependencies.ProductRepo()
    dependencies._inventory_repo = dependencies.InventoryRepo()
    dependencies._warehouse_repo = dependencies.WarehouseRepo()
    dependencies._document_repo = dependencies.DocumentRepo()

    # Reset services so they pick up the fresh repositories
    dependencies._product_service = None
    dependencies._inventory_service = None
    dependencies._warehouse_service = None
    dependencies._document_service = None
    dependencies._report_service = None
    dependencies._warehouse_operations_service = None
    yield


@pytest.fixture
def client():
    """FastAPI test client for integration tests using custom sync ASGI transport."""
    transport = SyncASGITransport(app=app)
    return httpx.Client(transport=transport, base_url="http://testserver")


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
    from app.repositories.sql.inventory_repo import InventoryRepo

    return InventoryService(InventoryRepo())


@pytest.fixture
def sample_product():
    """Fixture for a sample product."""
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
