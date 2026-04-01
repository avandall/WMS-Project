from __future__ import annotations

from typing import Any

from app.ai_engine.database import get_langchain_db
from app.ai_engine.llm import get_chat_model
from app.ai_engine.sql_exec import execute_readonly_sql
from app.ai_engine.settings import ai_engine_settings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

def _extract_sql(text: str) -> str:
    cleaned = text.strip()
    if "```" in cleaned:
        # Prefer fenced blocks like ```sql ... ```
        parts = cleaned.split("```")
        if len(parts) >= 3:
            cleaned = parts[1]
            # remove an optional language tag on first line
            cleaned = cleaned.split("\n", 1)[-1]
    return cleaned.strip().rstrip(";").strip()


def generate_sql_from_question(question: str) -> str:
    """Use an LLM to generate a safe, read-only SQL query for the WMS DB."""



    db = get_langchain_db()
    schema = db.get_table_info()
    max_rows = ai_engine_settings.db_max_rows

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """You are a Senior PostgreSQL Analyst. 
            Your goal is to write a syntactically correct SQL query based on the schema provided.
            Rules:
            - Use ONLY SELECT or WITH statements.
            - LIMIT results to {max_rows} unless specified.
            - Return ONLY the SQL code, no markdown, no explanation."""),
            # Kỹ thuật Few-shot: Cho AI xem ví dụ mẫu
            ("human", "Question: How many products are out of stock?\nSchema: Table 'products' (id, name, stock_count)"),
            ("ai", "SELECT COUNT(*) FROM products WHERE stock_count = 0;"),
            ("human", "Question: {question}\n\nDatabase schema:\n{schema}\n\nSQL:"),
        ]
    )

    llm = get_chat_model(temperature=0)  # deterministic output for SQL generation
    chain = prompt | llm | StrOutputParser()
    sql = chain.invoke({"question": question, "schema": schema, "max_rows": max_rows})
    return _extract_sql(sql)


def summarize_rows(question: str, sql: str, rows: list[dict[str, Any]]) -> str:
    """Turn SQL rows into a short customer-facing answer."""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """You are a professional WMS Support Agent.
            - Rule: Always answer in the SAME LANGUAGE as the customer's question.
            - If they ask in Vietnamese, reply in Vietnamese. If in English, reply in English.
            - Convert technical DB rows into a polite, natural language answer for the customer.
            - If rows are empty, politely inform them no data was found.
            - Use a helpful and professional tone."""),
            ("human", "Question: {question}\nData: {rows}\nAnswer:"),
        ]
    )

    llm = get_chat_model(temperature=0.7)  # some creativity allowed in summarization
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"question": question, "rows": rows})

def is_relevant_query(question: str) -> bool:
    """Check if a question is WMS-related (inventory/products/orders/warehouse)."""

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a security filter for a Warehouse Management System (WMS). "
                "Return ONLY True or False. True if the question is about inventory, products, documents/orders, customers, or warehouse data."
            ),
            ("human", "Question: {question}"),
        ]
    )

    llm = get_chat_model(temperature=0)
    chain = prompt | llm | StrOutputParser()
    result = (chain.invoke({"question": question}) or "").strip().lower()
    return result.startswith("true")


def handle_customer_chat_with_db(message: str) -> dict[str, Any]:
    """Entry point: customer message -> (SQL) -> DB rows -> final answer.

    If the message starts with `SQL:` (case-insensitive), the rest is treated as
    a direct SQL query (still restricted to SELECT/WITH).
    """
    stripped = message.strip()
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
