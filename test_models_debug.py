#!/usr/bin/env python3
"""Debug script to test model imports and relationships."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_models():
    """Test model imports and relationships."""
    try:
        from app.infrastructure.persistence.models import import_all_models
        import_all_models()
        
        from app.infrastructure.persistence.models import (
            Base, CustomerModel, DocumentModel, WarehouseModel, ProductModel
        )
        
        print("✅ All models imported successfully")
        print(f"✅ Base: {Base}")
        print(f"✅ CustomerModel: {CustomerModel}")
        print(f"✅ DocumentModel: {DocumentModel}")
        print(f"✅ WarehouseModel: {WarehouseModel}")
        print(f"✅ ProductModel: {ProductModel}")
        
        # Test creating tables
        from sqlalchemy import create_engine
        from app.core.settings import settings
        
        engine = create_engine(settings.database_url)
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_models()
    if success:
        print("\n🎉 Models test completed successfully!")
    else:
        print("\n💥 Models test failed!")
