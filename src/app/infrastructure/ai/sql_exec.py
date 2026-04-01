from __future__ import annotations

from typing import Any

from sqlalchemy import text

from app.core.database import engine
from app.infrastructure.ai.settings import ai_engine_settings


_DISALLOWED_TOKENS = (
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "truncate",
    "grant",
    "revoke",
)


def execute_readonly_sql(
    sql: str,
    params: dict[str, Any] | None = None,
    *,
    max_rows: int | None = None,
) -> list[dict[str, Any]]:
    """Execute a read-only SQL query and return up to `max_rows` rows.

Safety:
- Only allows `SELECT` / `WITH` queries
- Blocks common write/DDL keywords
- Blocks multiple statements (only a single statement is allowed)
"""

    cleaned = sql.strip().rstrip(";").strip()
    lowered = cleaned.lower()

    if not lowered.startswith(("select", "with")):
        raise ValueError("Only SELECT/WITH queries are allowed")
    if ";" in cleaned:
        raise ValueError("Multiple SQL statements are not allowed")
    if any(tok in lowered for tok in _DISALLOWED_TOKENS):
        raise ValueError("Only read-only queries are allowed")

    row_limit = max_rows if max_rows is not None else ai_engine_settings.db_max_rows

    with engine.connect() as conn:
        result = conn.execute(text(cleaned), params or {})
        rows = result.mappings().fetchmany(row_limit)
        return [dict(r) for r in rows]

