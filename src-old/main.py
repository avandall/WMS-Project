"""
Convenience entry point for running the API without modifying import paths.
Run from the WMS project root:

    uv run python main.py
    # or
    uv run uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
"""

import uvicorn
from app.core.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.api:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info",
    )
