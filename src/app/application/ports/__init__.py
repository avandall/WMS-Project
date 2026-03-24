"""Application ports (repository interfaces)."""

from app.repositories.interfaces.interfaces import (
    ICustomerRepo,
    IDocumentRepo,
    IInventoryRepo,
    IProductRepo,
    IUserRepo,
    IWarehouseRepo,
)

__all__ = [
    "ICustomerRepo",
    "IDocumentRepo",
    "IInventoryRepo",
    "IProductRepo",
    "IUserRepo",
    "IWarehouseRepo",
]
