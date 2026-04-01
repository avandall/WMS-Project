#!/usr/bin/env python3
"""Simple test to verify model imports without database connection."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all required imports work."""
    try:
        # Test basic imports
        from app.infrastructure.persistence.models import import_all_models
        from app.infrastructure.persistence.models import Base, CustomerModel, DocumentModel
        
        print("✅ Basic imports successful")
        
        # Test lazy loading
        import_all_models()
        print("✅ Model loading successful")
        
        # Test specific model imports
        from app.infrastructure.persistence.models.customer_table import CustomerModel
        from app.infrastructure.persistence.models.document_table import DocumentModel
        from app.infrastructure.persistence.models.warehouse_table import WarehouseModel
        from app.infrastructure.persistence.models.product_table import ProductModel
        
        print("✅ All model imports successful")
        
        # Test that models have correct attributes
        assert hasattr(CustomerModel, '__tablename__')
        assert hasattr(DocumentModel, '__tablename__')
        assert hasattr(WarehouseModel, '__tablename__')
        assert hasattr(ProductModel, '__tablename__')
        
        print("✅ Model structure validation passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n🎉 Import test completed successfully!")
    else:
        print("\n💥 Import test failed!")
