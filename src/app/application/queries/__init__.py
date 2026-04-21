"""Query pattern implementation for read operations."""

from .product_queries import GetProductQuery, GetAllProductsQuery
from .product_handlers import ProductQueryHandler

__all__ = [
    "GetProductQuery",
    "GetAllProductsQuery",
    "ProductQueryHandler",
]
