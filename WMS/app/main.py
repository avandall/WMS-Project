"""
Main entry point for PMKT Warehouse Management System.
Runs the FastAPI web server.

Usage:
    python app/main.py  (from WMS directory with venv activated)
    OR
    ./run_server.sh   (convenience script)
"""

import uvicorn
from app.core.settings import settings

if __name__ == "__main__":
    print("🚀 Starting Warehouse Management System...")
    print(f"📍 Host: {settings.host}")
    print(f"🔌 Port: {settings.port}")
    print(f"🔄 Reload: Enabled")
    print(f"🐛 Debug: {settings.debug}")
    print("-" * 50)

    uvicorn.run(
        "app.api:app",
        host=settings.host,
        port=settings.port,
        reload=True,  # Enable reload for development
        log_level="info",
    )
