"""
Basic usage examples for WMS AI Engine
"""
import os
import sys

from ai_engine import WMSEngine, ProcessingMode


def basic_rag_example():
    """Example of basic RAG usage"""
    print("=== Basic RAG Example ===")
    
    # Initialize engine in RAG mode
    engine = WMSEngine(mode=ProcessingMode.RAG)
    
    # Initialize with sample data
    engine.initialize_sample_data()
    
    # Test questions
    questions = [
        "What is a Warehouse Management System?",
        "How does inventory tracking work in WMS?",
        "What technologies are used in WMS?"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        result = engine.process_query(question)
        print(f"Response: {result['response']}")
        print(f"Success: {result['success']}")


def agent_example():
    """Example of agent usage with database tools"""
    print("\n=== Agent Example ===")
    
    # Initialize engine in Agent mode
    engine = WMSEngine(mode=ProcessingMode.AGENT)
    
    # Test questions that would use database tools
    questions = [
        "What is the inventory status for SKU12345?",
        "Check the status of order ORD-001",
        "What's in location A1-B2?"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        result = engine.process_query(question)
        print(f"Response: {result['response']}")
        print(f"Success: {result['success']}")


def hybrid_example():
    """Example of hybrid mode usage"""
    print("\n=== Hybrid Mode Example ===")
    
    # Initialize engine in Hybrid mode
    engine = WMSEngine(mode=ProcessingMode.HYBRID)
    engine.initialize_sample_data()
    
    # Test questions
    questions = [
        "How does WMS help with order fulfillment?",
        "What's the current inventory for SKU99999?"  # This would need database
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        result = engine.process_query(question)
        print(f"Response: {result['response']}")
        print(f"Mode used: {result['mode']}")


def custom_documents_example():
    """Example of adding custom documents"""
    print("\n=== Custom Documents Example ===")
    
    engine = WMSEngine(mode=ProcessingMode.RAG)
    
    # Add custom WMS documents
    custom_docs = [
        "Our warehouse uses a zone-based picking system with 5 main zones: A-E. Each zone specializes in different product categories.",
        "The receiving process involves 3 steps: unloading, inspection, and put-away. Average processing time is 2 hours per shipment.",
        "We use FIFO (First-In, First-Out) inventory rotation for perishable items and LIFO (Last-In, First-Out) for non-perishable goods."
    ]
    
    custom_metadatas = [
        {"source": "internal_docs", "category": "picking"},
        {"source": "internal_docs", "category": "receiving"},
        {"source": "internal_docs", "category": "inventory_rotation"}
    ]
    
    # Add documents
    success = engine.add_documents(custom_docs, custom_metadatas)
    print(f"Documents added successfully: {success}")
    
    # Test with custom data
    question = "How many picking zones do we have and what are they?"
    result = engine.process_query(question)
    print(f"\nQuestion: {question}")
    print(f"Response: {result['response']}")


if __name__ == "__main__":
    print("WMS AI Engine - Usage Examples")
    print("=" * 50)
    
    # Run examples (comment out if you don't have API keys set up)
    try:
        basic_rag_example()
        # agent_example()  # Requires database connection
        # hybrid_example()
        # custom_documents_example()
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure to set up your API keys in .env file")
