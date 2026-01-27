"""
Pytest configuration and fixtures for WMS tests.
Sets up common fixtures for testing.
"""

import pytest
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


# SQL test fixtures for unit/repo tests
@pytest.fixture(scope="function")
def test_engine():
    """Create a fresh test database engine for each test."""
    from sqlalchemy import create_engine
    from app.core.database import Base

    # Use in-memory SQLite for fast tests
    TEST_DATABASE_URL = "sqlite:///:memory:"

    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        future=True,
    )

    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=engine)
    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a fresh database session for each test."""
    from sqlalchemy.orm import sessionmaker

    TestSessionLocal = sessionmaker(
        bind=test_engine, autoflush=False, autocommit=False, future=True
    )
    session = TestSessionLocal()

    yield session

    session.close()


@pytest.fixture(autouse=True, scope="module")
def reset_db_for_integration_tests(request):
    """
    Auto-cleanup fixture for integration tests.
    Drops and recreates all tables once per test module.
    Seeds database with initial warehouses for tests that expect them.
    """
    # Only apply to integration tests (not unit or SQL tests)
    if "integration" not in str(request.fspath) and "test_db_isolation" not in str(
        request.fspath
    ):
        yield
        return

    # Import only when needed for integration tests
    from app.core.settings import settings
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.repositories.sql.models import Base, WarehouseModel, ProductModel

    # Create engine for integration test cleanup
    engine = create_engine(settings.database_url)

    # Drop and recreate all tables before each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Seed database with initial data for tests
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        # Create warehouses for tests that expect them
        warehouses = [
            WarehouseModel(warehouse_id=1, location="Test Warehouse 1"),
            WarehouseModel(warehouse_id=2, location="Test Warehouse 2"),
            WarehouseModel(warehouse_id=3, location="Test Warehouse 3"),
        ]
        for wh in warehouses:
            db.add(wh)

        # Create products for tests that expect them
        products = [
            ProductModel(
                product_id=101, name="Laptop", price=1500.00, description="Test laptop"
            ),
            ProductModel(
                product_id=102, name="Mouse", price=99.99, description="Test mouse"
            ),
            ProductModel(
                product_id=103,
                name="Keyboard",
                price=150.00,
                description="Test keyboard",
            ),
        ]
        for prod in products:
            db.add(prod)

        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

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
