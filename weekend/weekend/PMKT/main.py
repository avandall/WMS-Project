"""
Main entry point for PMKT Warehouse Management System.
Runs the FastAPI web server.
"""

import sys
import os
# Add parent directory to path for proper imports when running as script
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import uvicorn
from PMKT.api import app

if __name__ == "__main__":
    uvicorn.run(
        "PMKT.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )