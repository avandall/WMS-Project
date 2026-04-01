"""Role-based permissions for the WMS API."""
from enum import Enum
from typing import Set, Dict


class Permission(str, Enum):
    # Read permissions
    VIEW_PRODUCTS = "view_products"
    VIEW_INVENTORY = "view_inventory"
    VIEW_REPORTS = "view_reports"

    # Product/price management
    MANAGE_PRODUCTS = "manage_products"  # create/update/delete products
    EDIT_PRICES = "edit_prices"          # update product pricing

    # Warehouse operations
    MANAGE_WAREHOUSES = "manage_warehouses"  # create/delete/transfer warehouses

    # Document operations
    DOC_CREATE_IMPORT = "doc_create_import"
    DOC_CREATE_EXPORT = "doc_create_export"
    DOC_CREATE_TRANSFER = "doc_create_transfer"
    DOC_POST = "doc_post"  # approve/confirm/post document

    # User management
    MANAGE_USERS = "manage_users"


# Default role -> permissions mapping
# Extend or override as needed.
ROLE_PERMISSIONS: Dict[str, Set[Permission]] = {
    # Full access
    "admin": set(p for p in Permission),

    # Basic users can view product/inventory data
    "user": {Permission.VIEW_PRODUCTS, Permission.VIEW_INVENTORY, Permission.VIEW_REPORTS},

    # Sales can draft purchase/import documents
    "sales": {
        Permission.VIEW_PRODUCTS,
        Permission.VIEW_INVENTORY,
        Permission.VIEW_REPORTS,
        Permission.DOC_CREATE_IMPORT,
    },

    # Warehouse keeper confirms/approves documents and can transfer stock via documents
    "warehouse": {
        Permission.VIEW_PRODUCTS,
        Permission.VIEW_INVENTORY,
        Permission.VIEW_REPORTS,
        Permission.DOC_CREATE_TRANSFER,
        Permission.DOC_POST,
    },

    # Accountant can adjust prices
    "accountant": {
        Permission.VIEW_PRODUCTS,
        Permission.VIEW_INVENTORY,
        Permission.VIEW_REPORTS,
        Permission.EDIT_PRICES,
    },
}


def role_has_permissions(role: str, required: Set[Permission]) -> bool:
    if role == "admin":
        return True
    allowed = ROLE_PERMISSIONS.get(role, set())
    return required.issubset(allowed)
