from __future__ import annotations

from typing import Any

from app.infrastructure.ai.database import get_langchain_db
from app.infrastructure.ai.llm import get_chat_model
from app.infrastructure.ai.settings import ai_engine_settings
from app.infrastructure.ai.sql_exec import execute_readonly_sql


def _extract_sql(text: str) -> str:
    cleaned = (text or "").strip()
    if "```" in cleaned:
        parts = cleaned.split("```")
        if len(parts) >= 3:
            cleaned = parts[1]
            cleaned = cleaned.split("\n", 1)[-1]
    return cleaned.strip().rstrip(";").strip()


def generate_sql_from_question(question: str) -> str:
    """Use an LLM to generate a safe, read-only SQL query for the WMS DB."""

    try:
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Missing dependency: `langchain-core`.") from exc

    db = get_langchain_db()
    schema = db.get_table_info()
    max_rows = ai_engine_settings.db_max_rows

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a Senior PostgreSQL Analyst.\n"
                "Your goal is to write a syntactically correct SQL query based on the schema provided.\n"
                "Rules:\n"
                f"- Use ONLY SELECT or WITH statements.\n"
                f"- LIMIT results to {max_rows} unless specified.\n"
                "- Return ONLY the SQL code, no markdown, no explanation.",
            ),
            ("human", "Question: {question}\n\nDatabase schema:\n{schema}\n\nSQL:"),
        ]
    )

    llm = get_chat_model(temperature=0)
    chain = prompt | llm | StrOutputParser()
    sql = chain.invoke({"question": question, "schema": schema})
    return _extract_sql(sql)


def summarize_rows(question: str, sql: str, rows: list[dict[str, Any]]) -> str:
    """Turn SQL rows into a short customer-facing answer."""

    try:
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Missing dependency: `langchain-core`.") from exc

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a professional WMS Support Agent.\n"
                "- Always answer in the SAME LANGUAGE as the customer's question.\n"
                "- Convert technical DB rows into a polite, natural language answer.\n"
                "- If rows are empty, politely inform them no data was found.\n"
                "- Be concise.",
            ),
            ("human", "Question: {question}\nSQL: {sql}\nData: {rows}\nAnswer:"),
        ]
    )

    llm = get_chat_model(temperature=0.7)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"question": question, "sql": sql, "rows": rows})


def is_relevant_query(question: str) -> bool:
    """Light WMS relevance filter to reduce prompt-injection / off-topic requests."""

    try:
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Missing dependency: `langchain-core`.") from exc

    # First, check for obvious WMS-related keywords
    wms_keywords = [
        'product', 'inventory', 'warehouse', 'stock', 'item', 'goods',
        'customer', 'client', 'order', 'document', 'transaction',
        'import', 'export', 'transfer', 'sale', 'purchase',
        'quantity', 'price', 'cost', 'supplier', 'vendor',
        'location', 'storage', 'shelf', 'rack', 'bin',
        'shipment', 'delivery', 'receiving', 'dispatch',
        'database', 'data', 'record', 'table', 'query',
        'how many', 'count', 'list', 'show', 'find', 'search',
        # Vietnamese keywords
        'sản phẩm', 'hàng tồn kho', 'kho hàng', 'khách hàng', 'đơn hàng',
        'số lượng', 'giá', 'vị trí', 'danh sách', 'hiển thị', 'tìm kiếm',
        'bao nhiêu', 'cái', 'chiếc', 'món', 'hàng'
    ]
    
    question_lower = question.lower()
    
    # If any WMS keywords are found, consider it relevant
    if any(keyword in question_lower for keyword in wms_keywords):
        return True
    
    # If it's a short question (1-3 words), be more lenient and let LLM decide
    if len(question_lower.split()) <= 3:
        pass  # Continue to LLM evaluation
    else:
        # Additional check for business/financial context that might be WMS-related
        business_keywords = ['market', 'analysis', 'report', 'business', 'financial']
        if any(keyword in question_lower for keyword in business_keywords):
            # For business keywords, be more careful - use LLM to decide
            pass
        else:
            # If no relevant keywords at all, likely irrelevant
            return False
    
    # If no keywords found, use LLM for more nuanced判断
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a relevance filter for a Warehouse Management System (WMS). "
                "Determine if the question is related to warehouse operations, inventory management, "
                "products, customers, orders, or business data analysis. "
                "Be lenient - if the question could reasonably be about warehouse data, mark it relevant. "
                "Return ONLY 'true' or 'false' (lowercase). "
                "Examples of relevant: 'how many items', 'show me products', 'customer orders', 'inventory levels' "
                "Examples of irrelevant: 'weather today', 'sports scores', 'political news', 'personal advice'."
            ),
            ("human", "Question: {question}"),
        ]
    )

    llm = get_chat_model(temperature=0.1)  # Slightly higher temperature for more flexibility
    chain = prompt | llm | StrOutputParser()
    result = (chain.invoke({"question": question}) or "").strip().lower()
    
    # More lenient check - accept various true responses
    return result.startswith("true") or result == "yes" or result == "relevant"


def handle_customer_chat_with_db(message: str) -> dict[str, Any]:
    """Entry point: customer message -> (SQL) -> DB rows -> final answer."""

    stripped = (message or "").strip()
    greetings = {"hi", "hello", "hey", "hola", "สวัสดี", "xin chào", "xin chao"}
    if stripped.lower() in greetings:
        return {
            "sql": "",
            "rows": [],
            "answer": "Hi! Ask me about products, inventory, documents, customers… (read-only).",
        }

    if not is_relevant_query(stripped):
        return {
            "sql": "",
            "rows": [],
            "answer": "Xin lỗi, tôi chỉ có thể hỗ trợ các thông tin liên quan đến kho hàng và sản phẩm. Bạn vui lòng đặt câu hỏi khác nhé!",
        }

    if stripped.lower().startswith("sql:"):
        sql = stripped[4:].strip()
    else:
        sql = generate_sql_from_question(stripped)

    rows = execute_readonly_sql(sql)
    answer = summarize_rows(stripped, sql, rows)
    return {"sql": sql, "rows": rows, "answer": answer}

