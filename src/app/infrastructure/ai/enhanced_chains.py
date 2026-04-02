"""Enhanced AI chains with refactored imports, hardened SQL extraction, and structured logging."""

from __future__ import annotations

import re
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

# Consolidated imports to avoid repetition
from sqlalchemy import text
from fastapi.encoders import jsonable_encoder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Application imports
from app.core.database import engine
from app.core.logging import get_logger
from app.core.advanced_validation import SQLInjectionValidator, security_policy
from app.infrastructure.ai.database import get_langchain_db
from app.infrastructure.ai.llm import get_chat_model
from app.infrastructure.ai.settings import ai_engine_settings

logger = get_logger(__name__)

@dataclass
class SQLGenerationMetrics:
    """Metrics for SQL generation and execution."""
    question_length: int
    sql_length: int
    generation_time_ms: float
    execution_time_ms: float
    row_count: int
    validation_violations: List[str]
    success: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None

class SQLExtractor:
    """Hardened SQL extraction with support for multiple LLM output formats."""
    
    # Patterns for different SQL block formats
    SQL_BLOCK_PATTERNS = [
        # Standard markdown SQL blocks
        r'```sql\s*\n(.*?)\n```',
        r'```SQL\s*\n(.*?)\n```',
        r'```postgresql\s*\n(.*?)\n```',
        r'```postgres\s*\n(.*?)\n```',
        
        # Generic code blocks
        r'```\s*\n(.*?)\n```',
        
        # Plain SQL with markers
        r'SQL:\s*\n(.*?)(?=\n\n|\Z)',
        r'Query:\s*\n(.*?)(?=\n\n|\Z)',
        
        # Inline SQL (single line)
        r'`([^`]*(?:SELECT|WITH|INSERT|UPDATE|DELETE)[^`]*)`',
        r'"([^"]*(?:SELECT|WITH|INSERT|UPDATE|DELETE)[^"]*)"',
        r"'([^']*(?:SELECT|WITH|INSERT|UPDATE|DELETE)[^']*)'",
    ]
    
    # Patterns to clean up SQL
    CLEANUP_PATTERNS = [
        (r'^\s*--.*$', ''),  # Remove SQL comments
        (r'/\*.*?\*/', ''),  # Remove block comments
        (r'\s*\n\s*', ' '),  # Normalize whitespace
        (r'\s+', ' '),      # Collapse multiple spaces
        (r'^\s+|\s+$', ''),  # Trim leading/trailing
    ]
    
    @classmethod
    def extract_sql(cls, text: str) -> Tuple[str, List[str]]:
        """
        Extract SQL from LLM output with support for multiple formats.
        Returns (extracted_sql, list_of_issues).
        """
        start_time = time.time()
        issues = []
        
        try:
            logger.info("Starting SQL extraction", extra={
                "input_length": len(text),
                "input_preview": text[:200] + "..." if len(text) > 200 else text
            })
            
            if not text or not text.strip():
                issues.append("Empty input provided")
                return "", issues
            
            cleaned_text = text.strip()
            
            # Try each pattern to extract SQL
            extracted_sql = None
            pattern_used = None
            
            for i, pattern in enumerate(cls.SQL_BLOCK_PATTERNS):
                try:
                    match = re.search(pattern, cleaned_text, re.DOTALL | re.IGNORECASE)
                    if match:
                        extracted_sql = match.group(1).strip()
                        pattern_used = f"Pattern {i+1}: {pattern[:30]}..."
                        logger.info("SQL extracted using pattern", extra={
                            "pattern": pattern_used,
                            "extracted_length": len(extracted_sql)
                        })
                        break
                except Exception as e:
                    logger.warning("Pattern extraction failed", extra={
                        "pattern": pattern,
                        "error": str(e)
                    })
                    continue
            
            # If no pattern matched, assume the entire text is SQL
            if not extracted_sql:
                extracted_sql = cleaned_text
                pattern_used = "No pattern matched - using full text"
                logger.info("Using full text as SQL", extra={
                    "text_length": len(extracted_sql)
                })
            
            # Clean up the extracted SQL
            original_sql = extracted_sql
            for old_pattern, new_pattern in cls.CLEANUP_PATTERNS:
                try:
                    extracted_sql = re.sub(old_pattern, new_pattern, extracted_sql, flags=re.MULTILINE)
                except Exception as e:
                    logger.warning("SQL cleanup pattern failed", extra={
                        "pattern": old_pattern,
                        "error": str(e)
                    })
                    continue
            
            # Remove trailing semicolon and final cleanup
            extracted_sql = extracted_sql.rstrip(';').strip()
            
            # Validate the extracted SQL
            validation_issues = cls._validate_extracted_sql(extracted_sql)
            issues.extend(validation_issues)
            
            extraction_time = (time.time() - start_time) * 1000
            
            logger.info("SQL extraction completed", extra={
                "pattern_used": pattern_used,
                "original_length": len(original_sql),
                "final_length": len(extracted_sql),
                "extraction_time_ms": extraction_time,
                "issues": issues,
                "success": len(validation_issues) == 0
            })
            
            return extracted_sql, issues
            
        except Exception as e:
            extraction_time = (time.time() - start_time) * 1000
            error_msg = f"SQL extraction failed: {str(e)}"
            issues.append(error_msg)
            
            logger.error("SQL extraction failed", extra={
                "error": str(e),
                "stack_trace": traceback.format_exc(),
                "extraction_time_ms": extraction_time,
                "issues": issues
            })
            
            return "", issues
    
    @classmethod
    def _validate_extracted_sql(cls, sql: str) -> List[str]:
        """Validate extracted SQL for security and correctness."""
        issues = []
        
        if not sql:
            issues.append("Extracted SQL is empty")
            return issues
        
        # Check minimum length
        if len(sql) < 10:
            issues.append("SQL too short to be valid")
        
        # Check for SQL keywords
        sql_upper = sql.upper()
        if not any(keyword in sql_upper for keyword in ['SELECT', 'WITH']):
            issues.append("SQL does not contain SELECT or WITH")
        
        # Use advanced validation
        is_valid, violations = SQLInjectionValidator.validate_sql_structure(
            sql, allowed_operations={'SELECT', 'WITH'}
        )
        if not is_valid:
            issues.extend([f"Validation: {v}" for v in violations])
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'--.*drop',
            r'/\*.*drop',
            r'drop\s+table',
            r'delete\s+from',
            r'insert\s+into',
            r'update\s+.+set',
            r'create\s+table',
            r'alter\s+table',
            r'truncate\s+table',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, sql, re.IGNORECASE):
                issues.append(f"Suspicious pattern detected: {pattern}")
        
        return issues

class EnhancedAIChains:
    """Enhanced AI chains with structured logging and error handling."""
    
    def __init__(self):
        self.metrics_history: List[SQLGenerationMetrics] = []
        self.sql_extractor = SQLExtractor()
    
    def generate_sql_from_question(self, question: str) -> Tuple[str, SQLGenerationMetrics]:
        """
        Generate SQL from question with comprehensive logging and metrics.
        Returns (sql_query, metrics).
        """
        start_time = time.time()
        metrics = SQLGenerationMetrics(
            question_length=len(question),
            sql_length=0,
            generation_time_ms=0,
            execution_time_ms=0,
            row_count=0,
            validation_violations=[],
            success=False
        )
        
        try:
            logger.info("Starting SQL generation", extra={
                "question": question,
                "question_length": len(question),
                "max_rows": ai_engine_settings.db_max_rows
            })
            
            # Get database schema
            db = get_langchain_db()
            schema = db.get_table_info()
            
            # Create prompt
            prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    "You are a Senior PostgreSQL Analyst.\n"
                    "Your goal is to write a syntactically correct SQL query based on the schema provided.\n"
                    "Rules:\n"
                    f"- Use ONLY SELECT or WITH statements.\n"
                    f"- LIMIT results to {ai_engine_settings.db_max_rows} unless specified.\n"
                    "- Return ONLY the SQL code, no markdown, no explanation.",
                ),
                ("human", "Question: {question}\n\nDatabase schema:\n{schema}\n\nSQL:"),
            ])
            
            # Generate SQL
            llm = get_chat_model(temperature=0)
            chain = prompt | llm | StrOutputParser()
            
            generation_start = time.time()
            raw_sql = chain.invoke({"question": question, "schema": schema})
            generation_time = (time.time() - generation_start) * 1000
            
            logger.info("LLM SQL generation completed", extra={
                "raw_sql_length": len(raw_sql),
                "raw_sql_preview": raw_sql[:200] + "..." if len(raw_sql) > 200 else raw_sql,
                "generation_time_ms": generation_time
            })
            
            # Extract and validate SQL
            extracted_sql, validation_issues = self.sql_extractor.extract_sql(raw_sql)
            
            metrics.sql_length = len(extracted_sql)
            metrics.generation_time_ms = generation_time
            metrics.validation_violations = validation_issues
            
            if validation_issues:
                logger.warning("SQL validation issues found", extra={
                    "issues": validation_issues,
                    "extracted_sql": extracted_sql
                })
                metrics.success = False
                metrics.error_type = "Validation"
                metrics.error_message = "; ".join(validation_issues)
            else:
                metrics.success = True
                logger.info("SQL generation successful", extra={
                    "final_sql": extracted_sql,
                    "sql_length": len(extracted_sql),
                    "validation_issues": validation_issues
                })
            
            return extracted_sql, metrics
            
        except Exception as e:
            metrics.generation_time_ms = (time.time() - start_time) * 1000
            metrics.success = False
            metrics.error_type = type(e).__name__
            metrics.error_message = str(e)
            
            logger.error("SQL generation failed", extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "stack_trace": traceback.format_exc(),
                "question": question,
                "generation_time_ms": metrics.generation_time_ms
            })
            
            return "", metrics
        
        finally:
            self.metrics_history.append(metrics)
    
    def execute_sql_with_logging(self, sql: str, params: Dict[str, Any] = None) -> Tuple[List[Dict[str, Any]], float]:
        """
        Execute SQL with comprehensive logging and metrics.
        Returns (rows, execution_time_ms).
        """
        start_time = time.time()
        
        try:
            logger.info("Starting SQL execution", extra={
                "sql": sql,
                "params": params,
                "max_rows": ai_engine_settings.db_max_rows
            })
            
            # Validate SQL before execution
            is_valid, violations = SQLInjectionValidator.validate_sql_structure(
                sql, allowed_operations={'SELECT', 'WITH'}
            )
            if not is_valid:
                error_msg = f"SQL validation failed: {'; '.join(violations)}"
                logger.error("SQL validation failed", extra={
                    "violations": violations,
                    "sql": sql
                })
                raise ValueError(error_msg)
            
            # Execute SQL
            with engine.connect() as conn:
                result = conn.execute(
                    text(sql).execution_options(postgresql_readonly=True),
                    params or {}
                )
                rows = result.mappings().fetchmany(ai_engine_settings.db_max_rows)
                
                # Convert to JSON-safe format
                raw_data = [dict(r) for r in rows]
                safe_data = jsonable_encoder(raw_data)
            
            execution_time = (time.time() - start_time) * 1000
            
            logger.info("SQL execution completed", extra={
                "execution_time_ms": execution_time,
                "row_count": len(safe_data),
                "success": True
            })
            
            return safe_data, execution_time
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            logger.error("SQL execution failed", extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "stack_trace": traceback.format_exc(),
                "sql": sql,
                "params": params,
                "execution_time_ms": execution_time,
                "success": False
            })
            
            raise
    
    def summarize_rows_with_logging(self, question: str, sql: str, rows: List[Dict[str, Any]]) -> str:
        """Summarize rows with comprehensive logging."""
        start_time = time.time()
        
        try:
            logger.info("Starting row summarization", extra={
                "question": question,
                "sql": sql,
                "row_count": len(rows),
                "rows_preview": rows[:2] if rows else []
            })
            
            prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    "You are a professional WMS Support Agent.\n"
                    "- Always answer in the SAME LANGUAGE as the customer's question.\n"
                    "- Convert technical DB rows into a polite, natural language answer.\n"
                    "- If rows are empty, politely inform them no data was found.\n"
                    "- Be concise.",
                ),
                ("human", "Question: {question}\nSQL: {sql}\nData: {rows}\nAnswer:"),
            ])
            
            llm = get_chat_model(temperature=0.7)
            chain = prompt | llm | StrOutputParser()
            
            answer = chain.invoke({"question": question, "sql": sql, "rows": rows})
            summarization_time = (time.time() - start_time) * 1000
            
            logger.info("Row summarization completed", extra={
                "answer_length": len(answer),
                "answer_preview": answer[:200] + "..." if len(answer) > 200 else answer,
                "summarization_time_ms": summarization_time,
                "success": True
            })
            
            return answer
            
        except Exception as e:
            summarization_time = (time.time() - start_time) * 1000
            
            logger.error("Row summarization failed", extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "stack_trace": traceback.format_exc(),
                "question": question,
                "row_count": len(rows),
                "summarization_time_ms": summarization_time,
                "success": False
            })
            
            # Return a safe fallback message
            return "I apologize, but I encountered an error while processing your request. Please try again."
    
    def is_relevant_query_with_logging(self, question: str) -> bool:
        """Check query relevance with logging."""
        start_time = time.time()
        
        try:
            logger.info("Starting relevance check", extra={
                "question": question
            })
            
            prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    "You are a security filter for a Warehouse Management System (WMS). "
                    "Return ONLY True or False. True if the question is about inventory, products, documents/orders, customers, or warehouse data.",
                ),
                ("human", "Question: {question}"),
            ])
            
            llm = get_chat_model(temperature=0)
            chain = prompt | llm | StrOutputParser()
            
            result = (chain.invoke({"question": question}) or "").strip().lower()
            is_relevant = result.startswith("true")
            
            check_time = (time.time() - start_time) * 1000
            
            logger.info("Relevance check completed", extra={
                "is_relevant": is_relevant,
                "llm_result": result,
                "check_time_ms": check_time,
                "success": True
            })
            
            return is_relevant
            
        except Exception as e:
            check_time = (time.time() - start_time) * 1000
            
            logger.error("Relevance check failed", extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "stack_trace": traceback.format_exc(),
                "question": question,
                "check_time_ms": check_time,
                "success": False
            })
            
            # Default to not relevant on error
            return False
    
    def handle_customer_chat_with_db(self, message: str) -> Dict[str, Any]:
        """Enhanced customer chat handler with comprehensive logging and metrics."""
        request_start = time.time()
        
        try:
            logger.info("Starting customer chat request", extra={
                "message": message,
                "message_length": len(message)
            })
            
            # Handle greetings
            stripped = (message or "").strip()
            greetings = {"hi", "hello", "hey", "hola", "สวัสดี", "xin chào", "xin chao"}
            if stripped.lower() in greetings:
                response = {
                    "sql": "",
                    "rows": [],
                    "answer": "Hi! Ask me about products, inventory, documents, customers… (read-only).",
                    "metrics": SQLGenerationMetrics(
                        question_length=len(message),
                        sql_length=0,
                        generation_time_ms=0,
                        execution_time_ms=0,
                        row_count=0,
                        validation_violations=[],
                        success=True
                    )
                }
                
                logger.info("Greeting handled", extra={
                    "response_type": "greeting",
                    "total_time_ms": (time.time() - request_start) * 1000
                })
                
                return response
            
            # Check relevance
            if not self.is_relevant_query_with_logging(stripped):
                response = {
                    "sql": "",
                    "rows": [],
                    "answer": "Xin lỗi, tôi chỉ có thể hỗ trợ các thông tin liên quan đến kho hàng và sản phẩm. Bạn vui lòng đặt câu hỏi khác nhé!",
                    "metrics": SQLGenerationMetrics(
                        question_length=len(message),
                        sql_length=0,
                        generation_time_ms=0,
                        execution_time_ms=0,
                        row_count=0,
                        validation_violations=["Query not relevant to WMS"],
                        success=False,
                        error_type="Relevance",
                        error_message="Query not relevant to WMS"
                    )
                }
                
                logger.info("Irrelevant query handled", extra={
                    "response_type": "irrelevant",
                    "total_time_ms": (time.time() - request_start) * 1000
                })
                
                return response
            
            # Handle direct SQL
            if stripped.lower().startswith("sql:"):
                sql = stripped[4:].strip()
                sql_metrics = SQLGenerationMetrics(
                    question_length=len(message),
                    sql_length=len(sql),
                    generation_time_ms=0,
                    execution_time_ms=0,
                    row_count=0,
                    validation_violations=[],
                    success=False
                )
            else:
                # Generate SQL from question
                sql, sql_metrics = self.generate_sql_from_question(stripped)
            
            # Execute SQL if generation was successful
            if sql and sql_metrics.success:
                try:
                    rows, execution_time = self.execute_sql_with_logging(sql)
                    sql_metrics.execution_time_ms = execution_time
                    sql_metrics.row_count = len(rows)
                except Exception as e:
                    sql_metrics.success = False
                    sql_metrics.error_type = "Execution"
                    sql_metrics.error_message = str(e)
                    rows = []
                    execution_time = 0
            else:
                rows = []
                execution_time = 0
            
            # Generate summary
            answer = self.summarize_rows_with_logging(stripped, sql, rows)
            
            # Final response
            total_time = (time.time() - request_start) * 1000
            response = {
                "sql": sql,
                "rows": rows,
                "answer": answer,
                "metrics": sql_metrics
            }
            
            logger.info("Customer chat request completed", extra={
                "total_time_ms": total_time,
                "sql_success": sql_metrics.success,
                "row_count": len(rows),
                "answer_length": len(answer),
                "validation_violations": sql_metrics.validation_violations
            })
            
            return response
            
        except Exception as e:
            total_time = (time.time() - request_start) * 1000
            
            logger.error("Customer chat request failed", extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "stack_trace": traceback.format_exc(),
                "message": message,
                "total_time_ms": total_time,
                "success": False
            })
            
            # Return safe error response
            error_metrics = SQLGenerationMetrics(
                question_length=len(message),
                sql_length=0,
                generation_time_ms=0,
                execution_time_ms=0,
                row_count=0,
                validation_violations=["System error"],
                success=False,
                error_type="System",
                error_message=str(e)
            )
            
            return {
                "sql": "",
                "rows": [],
                "answer": "I apologize, but I encountered a system error. Please try again later.",
                "metrics": error_metrics
            }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring."""
        if not self.metrics_history:
            return {"message": "No metrics available"}
        
        successful_requests = [m for m in self.metrics_history if m.success]
        failed_requests = [m for m in self.metrics_history if not m.success]
        
        return {
            "total_requests": len(self.metrics_history),
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": len(successful_requests) / len(self.metrics_history) * 100,
            "avg_generation_time_ms": sum(m.generation_time_ms for m in self.metrics_history) / len(self.metrics_history),
            "avg_sql_length": sum(m.sql_length for m in self.metrics_history) / len(self.metrics_history),
            "avg_row_count": sum(m.row_count for m in self.metrics_history) / len(self.metrics_history),
            "common_errors": self._get_common_errors(failed_requests)
        }
    
    def _get_common_errors(self, failed_requests: List[SQLGenerationMetrics]) -> Dict[str, int]:
        """Get common error types from failed requests."""
        error_counts = {}
        for request in failed_requests:
            error_type = request.error_type or "Unknown"
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        return error_counts

# Global instance for backward compatibility
enhanced_chains = EnhancedAIChains()

# Backward compatibility functions
def generate_sql_from_question(question: str) -> str:
    """Backward compatibility wrapper."""
    sql, metrics = enhanced_chains.generate_sql_from_question(question)
    return sql

def summarize_rows(question: str, sql: str, rows: list[dict[str, Any]]) -> str:
    """Backward compatibility wrapper."""
    return enhanced_chains.summarize_rows_with_logging(question, sql, rows)

def is_relevant_query(question: str) -> bool:
    """Backward compatibility wrapper."""
    return enhanced_chains.is_relevant_query_with_logging(question)

def handle_customer_chat_with_db(message: str) -> dict[str, Any]:
    """Backward compatibility wrapper."""
    return enhanced_chains.handle_customer_chat_with_db(message)

def _extract_sql(text: str) -> str:
    """Backward compatibility wrapper."""
    sql, issues = SQLExtractor.extract_sql(text)
    return sql
