"""
Configuration settings for WMS AI Engine
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Central configuration class for WMS AI Engine"""
    
    # LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER")
    LLM_MODEL: str = os.getenv("LLM_MODEL")
    EVALUATOR_MODEL: str = os.getenv("EVALUATOR_MODEL")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE"))
    
    # Embedding Configuration
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL")
    
    # Database Configuration
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH")
    DB_CONNECTION_STRING: str = os.getenv("DB_CONNECTION_STRING")
    
    # Retrieval Configuration
    RETRIEVAL_K: int = int(os.getenv("RETRIEVAL_K"))
    BM25_WEIGHT: float = float(os.getenv("BM25_WEIGHT"))
    VECTOR_WEIGHT: float = float(os.getenv("VECTOR_WEIGHT"))
    
    # Evaluation Configuration
    QUALITY_THRESHOLD: float = float(os.getenv("QUALITY_THRESHOLD"))
    
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    
    @classmethod
    def get_llm_config(cls) -> Dict[str, Any]:
        """Get LLM configuration dictionary"""
        return {
            "model": cls.LLM_MODEL,
            "temperature": cls.TEMPERATURE,
            "api_key": cls.GROQ_API_KEY
        }
    
    @classmethod
    def get_evaluator_config(cls) -> Dict[str, Any]:
        """Get evaluator LLM configuration"""
        return {
            "model": cls.EVALUATOR_MODEL,
            "temperature": 0.0,
            "api_key": cls.GROQ_API_KEY
        }

settings = Settings()
