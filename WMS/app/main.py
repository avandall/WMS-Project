"""
Main entry point for PMKT Warehouse Management System.
Runs the FastAPI web server.
"""

import uvicorn
from app.core.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.api:app",
        host=settings.host,
        port=settings.port,
        reload=True,  # Enable reload for development
        log_level="info",
    )
