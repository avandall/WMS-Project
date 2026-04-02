"""Enhanced AI chains with refactored imports, hardened SQL extraction, and structured logging."""

# Import the enhanced implementation
from app.infrastructure.ai.enhanced_chains import (
    generate_sql_from_question,
    summarize_rows,
    is_relevant_query,
    handle_customer_chat_with_db,
    _extract_sql,
    EnhancedAIChains,
    SQLExtractor,
    SQLGenerationMetrics,
    enhanced_chains
)

# Re-export for backward compatibility
__all__ = [
    'generate_sql_from_question',
    'summarize_rows', 
    'is_relevant_query',
    'handle_customer_chat_with_db',
    '_extract_sql',
    'EnhancedAIChains',
    'SQLExtractor',
    'SQLGenerationMetrics',
    'enhanced_chains'
]

