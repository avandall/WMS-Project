from __future__ import annotations

import re  # 1. Thêm regex để check bảo mật chính xác hơn
from typing import Any

from sqlalchemy import text
from fastapi.encoders import jsonable_encoder # 2. Cần để xử lý kiểu dữ liệu lạ (Decimal, DateTime)

from app.core.database import engine
from app.infrastructure.ai.settings import ai_engine_settings

# Sử dụng ranh giới từ \b để tránh chặn nhầm 'created_at'
_DISALLOWED_PATTERN = re.compile(r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke)\b", re.IGNORECASE)


def execute_readonly_sql(
    sql: str,
    params: dict[str, Any] | None = None,
    *,
    max_rows: int | None = None,
) -> list[dict[str, Any]]:
    """
    Execute a read-only SQL query and return up to `max_rows` rows.
    """

    cleaned = sql.strip().rstrip(";").strip()
    lowered = cleaned.lower()

    # Kiểm tra khởi đầu bằng SELECT hoặc WITH
    if not lowered.startswith(("select", "with")):
        raise ValueError("Only SELECT/WITH queries are allowed")
    
    # Ngăn chặn nhiều câu lệnh (SQL Injection cơ bản)
    if ";" in cleaned:
        raise ValueError("Multiple SQL statements are not allowed")

    # 3. SỬA LỖI FALSE POSITIVE: Dùng regex thay vì 'in lowered'
    if _DISALLOWED_PATTERN.search(lowered):
        raise ValueError("Security violation: Only read-only queries are allowed")

    row_limit = max_rows if max_rows is not None else ai_engine_settings.db_max_rows

    with engine.connect() as conn:
        # Sử dụng execution_options để báo cho DB đây là giao dịch chỉ đọc (nếu DB hỗ trợ)
        result = conn.execute(
            text(cleaned).execution_options(postgresql_readonly=True), 
            params or {}
        )
        rows = result.mappings().fetchmany(row_limit)
        
        # 4. SỬA LỖI SERIALIZATION: Chuyển đổi dữ liệu sang dạng JSON-safe
        # jsonable_encoder giúp xử lý các kiểu Decimal từ Postgres thành float/string
        raw_data = [dict(r) for r in rows]
        return jsonable_encoder(raw_data)