#!/usr/bin/env python3
"""
Simple runner for WMS AI Engine Indexer
Easy-to-use interface for indexing and searching the WMS codebase.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_engine.indexer import WMSIndexer

def main():
    """Simple interface for the indexer."""
    print("🤖 WMS AI Engine - Codebase Indexer")
    print("=" * 50)
    
    # Initialize indexer
    indexer = WMSIndexer()
    
    while True:
        print("\n📋 Choose an action:")
        print("1. 🚀 Index codebase")
        print("2. 🔍 Search codebase")
        print("3. 📊 Show indexing status")
        print("4. ⚙️  Force reindex")
        print("5. ❌ Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            print("\n🚀 Starting indexing...")
            indexer.index_codebase()
            
        elif choice == "2":
            query = input("🔍 Enter search query: ").strip()
            if query:
                print(f"\n🔍 Searching for: '{query}'")
                results = indexer.search_codebase(query)
                
                if results:
                    print(f"\n📝 Found {len(results)} results:")
                    for i, doc in enumerate(results, 1):
                        file_path = doc.metadata.get('file_path', 'Unknown')
                        content_preview = doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
                        print(f"\n{i}. 📁 {file_path}")
                        print(f"   {content_preview}")
                else:
                    print("❌ No results found.")
            else:
                print("⚠️  Please enter a search query.")
                
        elif choice == "3":
            print("\n📊 Indexing Status:")
            status = indexer.get_indexing_status()
            print(f"Last indexed: {status.get('last_indexed', 'Never')}")
            print(f"Total stores: {status.get('total_stores', 0)}")
            print(f"Total chunks: {status.get('total_chunks', 0)}")
            
            if status.get('stores'):
                print("\n📚 Available stores:")
                for store_name, metadata in status['stores'].items():
                    print(f"  • {store_name}: {metadata.get('total_chunks', 0)} chunks")
                    
        elif choice == "4":
            print("\n⚙️  Force reindexing all files...")
            indexer.index_codebase(force_reindex=True)
            
        elif choice == "5":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("\n⚠️  Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main()
