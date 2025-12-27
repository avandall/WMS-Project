"""
FastAPI application for PMKT Warehouse Management System.
"""

from fastapi import FastAPI
from ..core.settings import settings
from .routers.products import router as products_router
from .routers.warehouses import router as warehouses_router
from .routers.inventory import router as inventory_router
from .routers.documents import router as documents_router
from .routers.reports import router as reports_router
from .warehouse_operations import router as warehouse_operations_router

app = FastAPI(
    title=settings.title,
    description=settings.description,
    version=settings.version,
    debug=settings.debug
)

# Include routers
app.include_router(products_router, prefix="/api/products", tags=["products"])
app.include_router(warehouses_router, prefix="/api/warehouses", tags=["warehouses"])
app.include_router(inventory_router, prefix="/api/inventory", tags=["inventory"])
app.include_router(documents_router, prefix="/api/documents", tags=["documents"])
app.include_router(reports_router, prefix="/api/reports", tags=["reports"])
app.include_router(warehouse_operations_router, prefix="/api", tags=["warehouse-operations"])