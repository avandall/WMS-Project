#!/usr/bin/env python3
"""
WMS Codebase Indexer - Advanced RAG Implementation
Indexes source code, documentation, and business logic for AI-powered code understanding.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# LangChain imports
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document

# Project structure
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
AI_ENGINE_DIR = PROJECT_ROOT / "ai_engine"
STORES_DIR = AI_ENGINE_DIR / "stores"
METADATA_DIR = AI_ENGINE_DIR / "metadata"

# Ensure directories exist
STORES_DIR.mkdir(exist_ok=True)
METADATA_DIR.mkdir(exist_ok=True)

class WMSIndexer:
    """Advanced codebase indexer for WMS project."""
    
    def __init__(self, 
                 embedding_model: str = "all-MiniLM-L6-v2",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 100):
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embeddings = None
        self.index_metadata = {}
        
    def _get_file_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Define file patterns for different types of content."""
        return {
            "python_code": {
                "path": SRC_DIR,
                "glob": "**/*.py",
                "language": Language.PYTHON,
                "parser_threshold": 500,
                "description": "Python source code"
            },
            "sql_schemas": {
                "path": SRC_DIR,
                "glob": "**/*.sql",
                "language": Language.SQL, 
                "parser_threshold": 200,
                "description": "SQL schemas and queries"
            },
            "config_files": {
                "path": PROJECT_ROOT,
                "glob": "*.toml",
                "language": Language.MARKDOWN,
                "parser_threshold": 100,
                "description": "Configuration files"
            },
            "docs": {
                "path": PROJECT_ROOT,
                "glob": "*.md",
                "language": Language.MARKDOWN,
                "parser_threshold": 300,
                "description": "Documentation files"
            },
            "requirements": {
                "path": PROJECT_ROOT,
                "glob": "requirements*.txt",
                "language": Language.MARKDOWN,
                "parser_threshold": 100,
                "description": "Dependencies and requirements"
            }
        }
    
    def _create_embeddings(self) -> HuggingFaceEmbeddings:
        """Initialize embedding model with caching."""
        if self.embeddings is None:
            print(f"🧠 Loading embedding model: {self.embedding_model}")
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.embedding_model,
                cache_folder=str(AI_ENGINE_DIR / "cache"),
                encode_kwargs={'normalize_embeddings': True}
            )
            print("✅ Embedding model loaded successfully")
        return self.embeddings
    
    def _load_documents(self, pattern_config: Dict[str, Any]) -> List[Document]:
        """Load documents based on pattern configuration."""
        try:
            loader = DirectoryLoader(
                str(pattern_config["path"]),
                glob=pattern_config["glob"],
                loader_cls=LanguageParser,
                loader_kwargs={
                    "language": pattern_config["language"], 
                    "parser_threshold": pattern_config["parser_threshold"]
                }
            )
            docs = loader.load()
            
            # Add metadata to each document
            for doc in docs:
                doc.metadata.update({
                    "content_type": pattern_config["description"],
                    "language": pattern_config["language"].value if hasattr(pattern_config["language"], 'value') else str(pattern_config["language"]),
                    "indexed_at": datetime.now().isoformat(),
                    "file_path": str(doc.metadata.get("source", ""))
                })
            
            return docs
            
        except Exception as e:
            print(f"⚠️  Error loading {pattern_config['description']}: {e}")
            return []
    
    def _split_documents(self, docs: List[Document], language: Language) -> List[Document]:
        """Split documents using language-aware chunking."""
        if not docs:
            return []
            
        print(f"✂️  Splitting {len(docs)} documents for {language.value}")
        
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=language,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            add_start_index=True
        )
        
        chunks = splitter.split_documents(docs)
        
        # Add chunk metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "chunk_id": f"{chunk.metadata.get('file_path', 'unknown')}_{i}",
                "chunk_index": i,
                "total_chunks": len(chunks)
            })
        
        print(f"✅ Created {len(chunks)} chunks")
        return chunks
    
    def _create_vector_store(self, chunks: List[Document], store_name: str) -> FAISS:
        """Create and save vector store."""
        if not chunks:
            print(f"⚠️  No chunks to process for {store_name}")
            return None
            
        print(f"🔍 Creating vector store for {store_name}...")
        
        embeddings = self._create_embeddings()
        vector_store = FAISS.from_documents(chunks, embeddings)
        
        # Save vector store
        store_path = STORES_DIR / store_name
        vector_store.save_local(str(store_path))
        
        print(f"💾 Vector store saved to {store_path}")
        return vector_store
    
    def _save_metadata(self, store_name: str, chunks: List[Document], pattern_config: Dict[str, Any]):
        """Save indexing metadata."""
        metadata = {
            "store_name": store_name,
            "created_at": datetime.now().isoformat(),
            "total_documents": len(set(doc.metadata.get("file_path") for doc in chunks)),
            "total_chunks": len(chunks),
            "embedding_model": self.embedding_model,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "pattern_config": pattern_config,
            "file_hashes": self._calculate_file_hashes(chunks)
        }
        
        metadata_file = METADATA_DIR / f"{store_name}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        self.index_metadata[store_name] = metadata
        print(f"📋 Metadata saved to {metadata_file}")
    
    def _calculate_file_hashes(self, chunks: List[Document]) -> Dict[str, str]:
        """Calculate MD5 hashes for source files."""
        file_hashes = {}
        for chunk in chunks:
            file_path = chunk.metadata.get("file_path", "")
            if file_path and file_path not in file_hashes:
                try:
                    with open(file_path, 'rb') as f:
                        file_hashes[file_path] = hashlib.md5(f.read()).hexdigest()
                except Exception as e:
                    print(f"⚠️  Could not hash {file_path}: {e}")
        return file_hashes
    
    def _should_reindex(self, store_name: str, pattern_config: Dict[str, Any]) -> bool:
        """Check if reindexing is needed based on file changes."""
        metadata_file = METADATA_DIR / f"{store_name}_metadata.json"
        
        if not metadata_file.exists():
            return True
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            old_hashes = metadata.get("file_hashes", {})
            
            # Check if any files have changed
            current_files = list(Path(pattern_config["path"]).glob(pattern_config["glob"]))
            for file_path in current_files:
                if file_path.is_file():
                    try:
                        with open(file_path, 'rb') as f:
                            current_hash = hashlib.md5(f.read()).hexdigest()
                        old_hash = old_hashes.get(str(file_path))
                        if current_hash != old_hash:
                            print(f"🔄 File changed: {file_path}")
                            return True
                    except Exception:
                        continue
            
            return False
            
        except Exception as e:
            print(f"⚠️  Error checking reindex status: {e}")
            return True
    
    def index_codebase(self, force_reindex: bool = False):
        """Index the entire WMS codebase."""
        print("🚀 Starting WMS codebase indexing...")
        print(f"📁 Project root: {PROJECT_ROOT}")
        print(f"📂 Source directory: {SRC_DIR}")
        
        patterns = self._get_file_patterns()
        total_chunks = 0
        indexed_stores = []
        
        for store_name, pattern_config in patterns.items():
            print(f"\n📚 Processing {pattern_config['description']}...")
            
            # Check if reindexing is needed
            if not force_reindex and not self._should_reindex(store_name, pattern_config):
                print(f"⏭️  Skipping {store_name} - no changes detected")
                continue
            
            # Load documents
            docs = self._load_documents(pattern_config)
            if not docs:
                print(f"⚠️  No documents found for {store_name}")
                continue
            
            # Split documents
            chunks = self._split_documents(docs, pattern_config["language"])
            if not chunks:
                continue
            
            # Create vector store
            vector_store = self._create_vector_store(chunks, store_name)
            if vector_store:
                # Save metadata
                self._save_metadata(store_name, chunks, pattern_config)
                indexed_stores.append(store_name)
                total_chunks += len(chunks)
        
        # Generate summary
        self._generate_indexing_summary(indexed_stores, total_chunks)
        
        print(f"\n🎉 Indexing completed! {total_chunks} total chunks indexed.")
        return indexed_stores
    
    def _generate_indexing_summary(self, indexed_stores: List[str], total_chunks: int):
        """Generate a summary of the indexing process."""
        summary = {
            "indexed_at": datetime.now().isoformat(),
            "total_stores": len(indexed_stores),
            "total_chunks": total_chunks,
            "stores": indexed_stores,
            "project_info": {
                "name": "WMS (Warehouse Management System)",
                "root": str(PROJECT_ROOT),
                "version": "1.0.0"
            }
        }
        
        summary_file = AI_ENGINE_DIR / "indexing_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Indexing summary saved to {summary_file}")
    
    def load_vector_store(self, store_name: str) -> Optional[FAISS]:
        """Load an existing vector store."""
        store_path = STORES_DIR / store_name
        if not store_path.exists():
            print(f"❌ Vector store not found: {store_path}")
            return None
        
        try:
            embeddings = self._create_embeddings()
            vector_store = FAISS.load_local(str(store_path), embeddings)
            print(f"✅ Loaded vector store: {store_name}")
            return vector_store
        except Exception as e:
            print(f"❌ Error loading vector store {store_name}: {e}")
            return None
    
    def search_codebase(self, query: str, store_name: str = "python_code", k: int = 5) -> List[Document]:
        """Search the indexed codebase."""
        vector_store = self.load_vector_store(store_name)
        if vector_store is None:
            print(f"❌ Cannot search {store_name} - vector store not available")
            return []
        
        try:
            results = vector_store.similarity_search(query, k=k)
            print(f"🔍 Found {len(results)} results for query: '{query}'")
            return results
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def get_indexing_status(self) -> Dict[str, Any]:
        """Get current indexing status."""
        status = {
            "last_indexed": None,
            "stores": {},
            "total_chunks": 0
        }
        
        for metadata_file in METADATA_DIR.glob("*_metadata.json"):
            store_name = metadata_file.stem.replace("_metadata", "")
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                status["stores"][store_name] = metadata
                status["total_chunks"] += metadata.get("total_chunks", 0)
                if status["last_indexed"] is None or metadata["created_at"] > status["last_indexed"]:
                    status["last_indexed"] = metadata["created_at"]
            except Exception as e:
                print(f"⚠️  Error reading metadata {metadata_file}: {e}")
        
        return status


def main():
    """Main function to run the indexer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="WMS Codebase Indexer")
    parser.add_argument("--force", action="store_true", help="Force reindex all files")
    parser.add_argument("--store", type=str, help="Index specific store only")
    parser.add_argument("--search", type=str, help="Search the codebase")
    parser.add_argument("--status", action="store_true", help="Show indexing status")
    
    args = parser.parse_args()
    
    indexer = WMSIndexer()
    
    if args.status:
        status = indexer.get_indexing_status()
        print("📊 Indexing Status:")
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    elif args.search:
        results = indexer.search_codebase(args.search)
        print("\n🔍 Search Results:")
        for i, doc in enumerate(results, 1):
            print(f"\n{i}. {doc.metadata.get('file_path', 'Unknown')}")
            print(f"   {doc.page_content[:200]}...")
    
    else:
        # Index the codebase
        indexer.index_codebase(force_reindex=args.force)


if __name__ == "__main__":
    main()