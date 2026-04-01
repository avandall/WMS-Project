#!/usr/bin/env python3
"""Debug script to check what tables are being created."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_tables():
    """Debug what tables are available."""
    from app.infrastructure.persistence.models import import_all_models, Base
    
    print("Importing all models...")
    import_all_models()
    
    print("\nAvailable tables:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")
    
    print(f"\nTotal tables: {len(Base.metadata.tables)}")
    
    # Check specifically for customers table
    if 'customers' in Base.metadata.tables:
        print("\n✅ 'customers' table found!")
    else:
        print("\n❌ 'customers' table NOT found!")
    
    # Check for documents table
    if 'documents' in Base.metadata.tables:
        print("✅ 'documents' table found!")
        docs_table = Base.metadata.tables['documents']
        print(f"  - Columns: {[col.name for col in docs_table.columns]}")
        for fk in docs_table.foreign_keys:
            print(f"  - Foreign key: {fk.column.name} -> {fk.column.table.name}")
    else:
        print("❌ 'documents' table NOT found!")

if __name__ == "__main__":
    debug_tables()
