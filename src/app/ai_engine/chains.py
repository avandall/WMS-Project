from __future__ import annotations

from typing import Any

from app.ai_engine.database import get_langchain_db
from app.ai_engine.llm import get_chat_model
from app.ai_engine.sql_exec import execute_readonly_sql


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

    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate

    db = get_langchain_db()
    schema = db.get_table_info()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a senior data analyst. "
                "Generate ONE PostgreSQL SQL query to answer the user question. "
                "Rules: read-only (SELECT/WITH only), no INSERT/UPDATE/DELETE/DDL, "
                "limit results to at most 50 rows unless asked otherwise, "
                "and output SQL only (no explanation).",
            ),
            (
                "human",
                "Question: {question}\n\nDatabase schema:\n{schema}\n\nSQL:",
            ),
        ]
    )

    llm = get_chat_model()
    chain = prompt | llm | StrOutputParser()
    sql = chain.invoke({"question": question, "schema": schema})
    return _extract_sql(sql)


def summarize_rows(question: str, sql: str, rows: list[dict[str, Any]]) -> str:
    """Turn SQL rows into a short customer-facing answer."""

    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful WMS support agent. "
                "Answer using the query result. Be concise and accurate. "
                "If there are no rows, say you couldn't find matching data.",
            ),
            (
                "human",
                "Customer question: {question}\nSQL used: {sql}\nRows: {rows}\n\nAnswer:",
            ),
        ]
    )

    llm = get_chat_model()
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"question": question, "sql": sql, "rows": rows})


def handle_customer_chat_with_db(message: str) -> dict[str, Any]:
    """Entry point: customer message -> (SQL) -> DB rows -> final answer.

    If the message starts with `SQL:` (case-insensitive), the rest is treated as
    a direct SQL query (still restricted to SELECT/WITH).
    """

    stripped = message.strip()
    if stripped.lower().startswith("sql:"):
        sql = stripped[4:].strip()
    else:
        sql = generate_sql_from_question(stripped)

    rows = execute_readonly_sql(sql)
    answer = summarize_rows(stripped, sql, rows)

    return {"sql": sql, "rows": rows, "answer": answer}
