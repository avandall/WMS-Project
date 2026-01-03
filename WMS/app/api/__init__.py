"""
FastAPI application for PMKT Warehouse Management System.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from ..core.settings import settings
from ..core.database import init_db
from .routers.products import router as products_router
from .routers.warehouses import router as warehouses_router
from .routers.inventory import router as inventory_router
from .routers.documents import router as documents_router
from .routers.reports import router as reports_router
from .warehouse_operations import router as warehouse_operations_router
from ..exceptions.business_exceptions import (
    EntityNotFoundError,
    ValidationError,
    WarehouseNotFoundError,
    InvalidQuantityError,
    InsufficientStockError,
    ProductNotFoundError,
    DocumentNotFoundError,
    InvalidDocumentStatusError,
    EntityAlreadyExistsError,
)

app = FastAPI(
    title=settings.title,
    description=settings.description,
    version=settings.version,
    debug=settings.debug,
)

# Ensure database tables exist at startup
init_db()


# Exception handlers
@app.exception_handler(EntityNotFoundError)
async def entity_not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(WarehouseNotFoundError)
async def warehouse_not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ProductNotFoundError)
async def product_not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(DocumentNotFoundError)
async def document_not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(InvalidQuantityError)
async def invalid_quantity_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(InsufficientStockError)
async def insufficient_stock_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(InvalidDocumentStatusError)
async def invalid_document_status_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(EntityAlreadyExistsError)
async def entity_already_exists_handler(request, exc):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


# Include routers
app.include_router(products_router, prefix="/api/products", tags=["products"])
app.include_router(warehouses_router, prefix="/api/warehouses", tags=["warehouses"])
app.include_router(inventory_router, prefix="/api/inventory", tags=["inventory"])
app.include_router(documents_router, prefix="/api/documents", tags=["documents"])
app.include_router(reports_router, prefix="/api/reports", tags=["reports"])
app.include_router(
    warehouse_operations_router, prefix="/api", tags=["warehouse-operations"]
)
