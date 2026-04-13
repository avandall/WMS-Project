"""
Quick Start Guide for WMS AI Engine
"""
import os
import sys

def quick_start():
    """Simple quick start example"""
    print("WMS AI Engine - Quick Start")
    print("=" * 30)
    
    # Step 1: Import
    from ai_engine import WMSEngine, ProcessingMode
    
    # Step 2: Initialize engine
    print("1. Initializing engine...")
    engine = WMSEngine(mode=ProcessingMode.RAG)
    
    # Step 3: Add sample data
    print("2. Loading sample data...")
    engine.initialize_sample_data()
    
    # Step 4: Ask questions
    print("3. Asking questions...")
    
    questions = [
        "What is a Warehouse Management System?",
        "How does inventory tracking work?",
        "What is order fulfillment?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\nQuestion {i}: {question}")
        result = engine.process_query(question)
        print(f"Answer: {result['response'][:100]}...")
        print(f"Success: {result['success']}")
    
    print("\nQuick start complete!")

if __name__ == "__main__":
    try:
        quick_start()
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure .env file exists with GROQ_API_KEY")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Check that all environment variables are set")
