#!/usr/bin/env python3
"""Simple functional test to verify setup works."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_functional_setup():
    """Test functional test setup."""
    try:
        # Test imports
        from app.application.services.product_service import ProductService
        from app.application.services.warehouse_service import WarehouseService
        from app.application.services.inventory_service import InventoryService
        from app.application.services.document_service import DocumentService
        from app.infrastructure.persistence.repositories.product_repo import ProductRepo
        from app.infrastructure.persistence.repositories.warehouse_repo import WarehouseRepo
        from app.infrastructure.persistence.repositories.inventory_repo import InventoryRepo
        from app.infrastructure.persistence.repositories.document_repo import DocumentRepo
        from app.domain.entities.document import DocumentType
        from app.domain.exceptions import ValidationError, InvalidQuantityError
        
        print("✅ All imports successful")
        
        # Test database setup
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.infrastructure.persistence.models import import_all_models, Base
        
        # Create SQLite database
        engine = create_engine("sqlite:///test_functional.db", echo=False)
        
        # Import models and create tables
        import_all_models()
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables created successfully")
        
        # Create session
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Create repositories
        product_repo = ProductRepo(db)
        warehouse_repo = WarehouseRepo(db)
        inventory_repo = InventoryRepo(db)
        document_repo = DocumentRepo(db)
        
        # Create services
        product_service = ProductService(product_repo, inventory_repo)
        warehouse_service = WarehouseService(warehouse_repo, product_repo, inventory_repo)
        inventory_service = InventoryService(inventory_repo, product_repo, warehouse_repo)
        document_service = DocumentService(document_repo, warehouse_service, product_repo, inventory_repo)
        
        print("✅ Services created successfully")
        
        # Test basic operations
        from app.domain.entities.product import Product
        from app.domain.entities.warehouse import Warehouse
        
        # Create test product
        product = Product(
            product_id=1,
            name="Test Product",
            description="Test Description",
            price=10.0
        )
        product_repo.save(product)
        
        # Create test warehouse
        warehouse = Warehouse(
            warehouse_id=1,
            location="Test Warehouse"
        )
        warehouse_repo.save(warehouse)
        
        print("✅ Basic operations successful")
        
        db.close()
        os.remove("test_functional.db")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_functional_setup()
    if success:
        print("\n🎉 Functional test setup completed successfully!")
    else:
        print("\n💥 Functional test setup failed!")
