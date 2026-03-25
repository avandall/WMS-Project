"""Application ports (repository interfaces)."""

from app.repositories.interfaces.interfaces import (
    IAuditEventRepo,
    ICustomerRepo,
    IDocumentRepo,
    IInventoryRepo,
    IPositionRepo,
    IProductRepo,
    IUserRepo,
    IWarehouseRepo,
)

__all__ = [
    "IAuditEventRepo",
    "ICustomerRepo",
    "IDocumentRepo",
    "IInventoryRepo",
    "IPositionRepo",
    "IProductRepo",
    "IUserRepo",
    "IWarehouseRepo",
]
