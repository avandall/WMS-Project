"""
Helper utilities for WMS AI Engine
"""
import time
import os
from typing import List, Dict, Any, Optional
from pathlib import Path


def ensure_directory_exists(path: str) -> None:
    """Ensure directory exists, create if it doesn't"""
    Path(path).mkdir(parents=True, exist_ok=True)


def format_documents_for_display(documents: List[str], max_length: int = 500) -> str:
    """Format documents for display with truncation"""
    formatted_docs = []
    for i, doc in enumerate(documents, 1):
        truncated = doc[:max_length] + "..." if len(doc) > max_length else doc
        formatted_docs.append(f"Document {i}:\n{truncated}")
    return "\n\n".join(formatted_docs)


def retry_with_backoff(func, max_retries: int = 3, backoff_factor: float = 1.0):
    """Retry function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            wait_time = backoff_factor * (2 ** attempt)
            time.sleep(wait_time)


def validate_api_keys() -> Dict[str, bool]:
    """Validate required API keys are present"""
    from ..config import settings
    
    validation_results = {
        "groq": bool(settings.GROQ_API_KEY)
    }
    
    return validation_results


def sanitize_text(text: str) -> str:
    """Sanitize text for processing"""
    # Remove excessive whitespace
    text = ' '.join(text.split())
    # Remove potentially harmful characters (basic sanitization)
    dangerous_chars = ['<', '>', '&', '"', "'"]
    for char in dangerous_chars:
        text = text.replace(char, '')
    return text


def calculate_retrieval_metrics(retrieved_docs: List[str], relevant_docs: List[str]) -> Dict[str, float]:
    """Calculate basic retrieval metrics"""
    if not relevant_docs:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    
    # Simple exact match for demonstration
    retrieved_set = set(retrieved_docs)
    relevant_set = set(relevant_docs)
    
    true_positives = len(retrieved_set & relevant_set)
    false_positives = len(retrieved_set - relevant_set)
    false_negatives = len(relevant_set - retrieved_set)
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


def create_wms_sample_data() -> List[Dict[str, Any]]:
    """Create sample WMS data for testing"""
    return [
        {
            "text": "Warehouse Management System (WMS) is a software solution that helps manage and optimize daily warehouse operations including inventory management, order fulfillment, and shipping.",
            "metadata": {"source": "wms_docs", "category": "overview"}
        },
        {
            "text": "Inventory tracking in WMS involves real-time monitoring of stock levels, locations, and movements. This helps prevent stockouts and overstocking situations.",
            "metadata": {"source": "wms_docs", "category": "inventory"}
        },
        {
            "text": "Order fulfillment process in WMS includes order picking, packing, and shipping. The system optimizes picking routes and assigns tasks to warehouse staff.",
            "metadata": {"source": "wms_docs", "category": "fulfillment"}
        },
        {
            "text": "WMS provides real-time visibility into warehouse operations through dashboards and reports. Managers can track KPIs like order accuracy, fulfillment time, and inventory turnover.",
            "metadata": {"source": "wms_docs", "category": "reporting"}
        },
        {
            "text": "Barcode scanning and RFID technology are integrated with WMS to automate data capture and reduce manual errors in inventory management.",
            "metadata": {"source": "wms_docs", "category": "technology"}
        }
    ]
