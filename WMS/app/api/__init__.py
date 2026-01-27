"""
FastAPI application for PMKT Warehouse Management System.
"""

import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ..core.settings import settings
from ..core.database import init_db, check_db_connection
from ..core.logging import setup_logging, set_request_id, clear_request_id, get_logger
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

# Initialize logging
setup_logging(level="INFO")
logger = get_logger(__name__)

app = FastAPI(
    title=settings.title,
    description=settings.description,
    version=settings.version,
    debug=settings.debug,
)

# Configure CORS (CRITICAL for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Configure specific origins in production
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Ensure database tables exist at startup
init_db()


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """
    Add request ID to all requests for tracing.
    Request ID is included in all log messages for correlation.
    """
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    set_request_id(request_id)
    
    logger.debug(f"Request started: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        logger.debug(f"Request completed: {request.method} {request.url.path} - Status {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {request.method} {request.url.path} - {type(e).__name__}: {str(e)}")
        raise
    finally:
        clear_request_id()


@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Health check endpoint for load balancers and monitoring.
    Returns service status and database connectivity.
    """
    db_healthy = check_db_connection()
    
    status = "healthy" if db_healthy else "unhealthy"
    status_code = 200 if db_healthy else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": status,
            "database": "connected" if db_healthy else "disconnected",
            "version": settings.version,
        }
    )


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint providing API information and available endpoints.
    """
    return {
        "message": "Welcome to PMKT Warehouse Management System API",
        "version": settings.version,
        "documentation": "/docs",
        "health_check": "/health",
        "api_endpoints": {
            "products": "/api/products",
            "warehouses": "/api/warehouses", 
            "inventory": "/api/inventory",
            "documents": "/api/documents",
            "reports": "/api/reports",
            "warehouse_operations": "/api/warehouse-operations"
        }
    }


@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    logger.info(f"Starting {settings.title} v{settings.version}")
    logger.info(f"Debug mode: {settings.debug}")
    if check_db_connection():
        logger.info("Database connection: OK")
    else:
        logger.error("Database connection: FAILED")


@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info("Shutting down application")



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
