"""
Complete Usage Guide for WMS AI Engine
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai_engine import WMSEngine, ProcessingMode


def setup_environment():
    """Step 1: Setup environment variables"""
    print("=== Step 1: Environment Setup ===")
    print("Make sure you have a .env file with these variables:")
    print("""
    GROQ_API_KEY=your_groq_api_key_here
    LLM_PROVIDER=groq
    LLM_MODEL=llama-3.1-8b-instant
    EVALUATOR_MODEL=llama-3.3-70b-versatile
    TEMPERATURE=0.0
    EMBEDDING_PROVIDER=huggingface
    EMBEDDING_MODEL=all-MiniLM-L6-v2
    VECTOR_DB_PATH=./wms_chroma_db
    DB_CONNECTION_STRING=postgresql://wms_user:wms_password@localhost:5433/warehouse_db
    RETRIEVAL_K=3
    BM25_WEIGHT=0.4
    VECTOR_WEIGHT=0.6
    QUALITY_THRESHOLD=7.0
    """)
    print()


def basic_rag_usage():
    """Step 2: Basic RAG usage"""
    print("=== Step 2: Basic RAG Usage ===")
    
    try:
        # Initialize engine in RAG mode
        engine = WMSEngine(mode=ProcessingMode.RAG)
        print("Engine initialized successfully!")
        
        # Initialize with sample WMS data
        success = engine.initialize_sample_data()
        if success:
            print("Sample WMS data loaded successfully!")
        else:
            print("Failed to load sample data")
            return
        
        # Test questions about WMS
        questions = [
            "What is a Warehouse Management System?",
            "How does inventory tracking work in WMS?",
            "What technologies are used in WMS?",
            "What is order fulfillment process?"
        ]
        
        print("\nTesting RAG queries:")
        for i, question in enumerate(questions, 1):
            print(f"\n--- Query {i} ---")
            print(f"Question: {question}")
            
            result = engine.process_query(question)
            print(f"Response: {result['response'][:200]}...")
            print(f"Success: {result['success']}")
            print(f"Mode: {result['mode']}")
            
    except Exception as e:
        print(f"Error in basic RAG usage: {e}")
        print("Make sure your .env file is properly configured!")
    
    print()


def agent_usage():
    """Step 3: Agent usage with database tools"""
    print("=== Step 3: Agent Usage ===")
    
    try:
        # Initialize engine in Agent mode
        engine = WMSEngine(mode=ProcessingMode.AGENT)
        print("Agent engine initialized successfully!")
        
        # Test questions that would use database tools
        questions = [
            "What is the inventory status for SKU12345?",
            "Check the status of order ORD-001",
            "What's in location A1-B2?",
            "How many items are in zone A?"
        ]
        
        print("\nTesting Agent queries:")
        for i, question in enumerate(questions, 1):
            print(f"\n--- Query {i} ---")
            print(f"Question: {question}")
            
            result = engine.process_query(question)
            print(f"Response: {result['response']}")
            print(f"Success: {result['success']}")
            print(f"Mode: {result['mode']}")
            
    except Exception as e:
        print(f"Error in agent usage: {e}")
        print("Note: Agent queries require database connection")
    
    print()


def hybrid_usage():
    """Step 4: Hybrid mode usage"""
    print("=== Step 4: Hybrid Mode Usage ===")
    
    try:
        # Initialize engine in Hybrid mode
        engine = WMSEngine(mode=ProcessingMode.HYBRID)
        engine.initialize_sample_data()
        print("Hybrid engine initialized successfully!")
        
        # Test questions
        questions = [
            "How does WMS help with order fulfillment?",  # Should use RAG
            "What's the current inventory for SKU99999?"   # Should fallback to agent
        ]
        
        print("\nTesting Hybrid queries:")
        for i, question in enumerate(questions, 1):
            print(f"\n--- Query {i} ---")
            print(f"Question: {question}")
            
            result = engine.process_query(question)
            print(f"Response: {result['response'][:200]}...")
            print(f"Mode used: {result['mode']}")
            print(f"Success: {result['success']}")
            
    except Exception as e:
        print(f"Error in hybrid usage: {e}")
    
    print()


def custom_documents_usage():
    """Step 5: Adding custom documents"""
    print("=== Step 5: Custom Documents Usage ===")
    
    try:
        engine = WMSEngine(mode=ProcessingMode.RAG)
        
        # Add custom WMS documents
        custom_docs = [
            "Our warehouse uses a zone-based picking system with 5 main zones: A-E. Each zone specializes in different product categories.",
            "The receiving process involves 3 steps: unloading, inspection, and put-away. Average processing time is 2 hours per shipment.",
            "We use FIFO (First-In, First-Out) inventory rotation for perishable items and LIFO (Last-In, First-Out) for non-perishable goods.",
            "Our warehouse operates 24/7 with 3 shifts: morning (6am-2pm), evening (2pm-10pm), and night (10pm-6am).",
            "Safety protocols require all staff to wear PPE including safety vests, hard hats, and steel-toed boots at all times."
        ]
        
        custom_metadatas = [
            {"source": "internal_docs", "category": "picking", "department": "operations"},
            {"source": "internal_docs", "category": "receiving", "department": "operations"},
            {"source": "internal_docs", "category": "inventory", "department": "warehouse"},
            {"source": "internal_docs", "category": "operations", "department": "hr"},
            {"source": "internal_docs", "category": "safety", "department": "compliance"}
        ]
        
        # Add documents
        success = engine.add_documents(custom_docs, custom_metadatas)
        print(f"Documents added successfully: {success}")
        
        if success:
            # Test with custom data
            questions = [
                "How many picking zones do we have and what are they?",
                "What are the steps in the receiving process?",
                "What inventory rotation methods do we use?",
                "What are the working hours and shifts?",
                "What safety equipment is required?"
            ]
            
            print("\nTesting with custom documents:")
            for i, question in enumerate(questions, 1):
                print(f"\n--- Query {i} ---")
                print(f"Question: {question}")
                
                result = engine.process_query(question)
                print(f"Response: {result['response'][:150]}...")
                print(f"Success: {result['success']}")
                
    except Exception as e:
        print(f"Error with custom documents: {e}")
    
    print()


def web_documents_usage():
    """Step 6: Adding documents from web"""
    print("=== Step 6: Web Documents Usage ===")
    
    try:
        engine = WMSEngine(mode=ProcessingMode.RAG)
        
        # Add documents from web URLs (example URLs)
        urls = [
            "https://lilianweng.github.io/posts/2023-06-23-agent/"  # Example URL about AI agents
        ]
        
        print("Adding documents from web URLs...")
        success = engine.add_web_documents(urls)
        print(f"Web documents added successfully: {success}")
        
        if success:
            # Test with web data
            question = "What are the key components of AI agents according to the article?"
            print(f"\nQuestion: {question}")
            
            result = engine.process_query(question)
            print(f"Response: {result['response'][:200]}...")
            print(f"Success: {result['success']}")
            
    except Exception as e:
        print(f"Error with web documents: {e}")
        print("Note: Web scraping requires internet connection")
    
    print()


def engine_info():
    """Step 7: Get engine information"""
    print("=== Step 7: Engine Information ===")
    
    try:
        engine = WMSEngine(mode=ProcessingMode.RAG)
        info = engine.get_engine_info()
        
        print("Current Engine Configuration:")
        for key, value in info.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"Error getting engine info: {e}")
    
    print()


def main():
    """Complete usage guide"""
    print("WMS AI Engine - Complete Usage Guide")
    print("=" * 50)
    
    # Run all usage examples
    setup_environment()
    basic_rag_usage()
    agent_usage()
    hybrid_usage()
    custom_documents_usage()
    web_documents_usage()
    engine_info()
    
    print("=== Usage Guide Complete ===")
    print("\nTo run individual examples:")
    print("1. Make sure .env file is configured")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run this script: python examples/complete_usage_guide.py")


if __name__ == "__main__":
    main()
