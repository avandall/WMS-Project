#!/usr/bin/env python3
"""Debug conftest.py table creation."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_conftest():
    """Debug conftest table creation."""
    from app.infrastructure.persistence.models import import_all_models, Base
    
    print("Before import_all_models:")
    print(f"Tables: {list(Base.metadata.tables.keys())}")
    
    # Import models
    import_all_models()
    
    print("\nAfter import_all_models:")
    print(f"Tables: {list(Base.metadata.tables.keys())}")
    
    # Check specifically for customers table
    if 'customers' in Base.metadata.tables:
        print("\n✅ 'customers' table found!")
    else:
        print("\n❌ 'customers' table NOT found!")
    
    # Check for documents table
    if 'documents' in Base.metadata.tables:
        print("✅ 'documents' table found!")
        docs_table = Base.metadata.tables['documents']
        print(f"  - Foreign keys: {[fk.column.name for fk in docs_table.foreign_keys]}")
    else:
        print("❌ 'documents' table NOT found!")
    
    # Try creating tables
    try:
        from sqlalchemy import create_engine
        engine = create_engine("sqlite:///debug.db", echo=False)
        Base.metadata.create_all(bind=engine)
        print("\n✅ Tables created successfully!")
        os.remove("debug.db")
    except Exception as e:
        print(f"\n❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_conftest()
