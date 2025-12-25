"""
FastAPI application for PMKT Warehouse Management System.
Provides REST API endpoints for warehouse operations.
"""

from fastapi import FastAPI, Depends
from .dependencies import get_product_service, get_inventory_service, get_warehouse_service, get_document_service, get_report_service
from .routers import products, inventory, warehouses, documents, reports

app = FastAPI(
    title="PMKT Warehouse Management System",
    description="REST API for warehouse operations using Clean Architecture",
    version="1.0.0",
)

# Include routers
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["inventory"])
app.include_router(warehouses.router, prefix="/api/v1/warehouses", tags=["warehouses"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "PMKT Warehouse Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}