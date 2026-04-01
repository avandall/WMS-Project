from functools import lru_cache

from app.core.database import engine


@lru_cache(maxsize=1)
def get_langchain_db():
    """Connect LangChain to the WMS database (via the existing SQLAlchemy engine)."""

    try:
        from langchain_community.utilities import SQLDatabase
    except Exception as e:  # pragma: no cover
        raise RuntimeError("Missing dependency: `langchain-community`.") from e

    return SQLDatabase(engine)
