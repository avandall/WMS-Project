"""
Inventory Report classes for PMKT Warehouse Management System.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from app.models.inventory_domain import InventoryItem as InventoryItemDomain

@dataclass
class InventoryReportItem:
    """Represents an item in inventory report."""
    product_id: int
    quantity: int
    product_name: Optional[str] = None
    unit_value: Optional[float] = None

    @property
    def total_value(self) -> Optional[float]:
        if self.unit_value is not None:
            return self.quantity * self.unit_value
        return None

@dataclass
class WarehouseInventoryReport:
    """Report for a specific warehouse's inventory."""
    warehouse_id: int
    warehouse_location: str
    items: List[InventoryReportItem]
    low_stock_items: List[InventoryReportItem]
    generated_at: datetime

    @property
    def total_items(self) -> int:
        return len(self.items)

    @property
    def total_quantity(self) -> int:
        return sum(item.quantity for item in self.items)

    @property
    def total_value(self) -> Optional[float]:
        values = [item.total_value for item in self.items if item.total_value is not None]
        return sum(values) if values else None

@dataclass
class TotalInventoryReport:
    """Report for total inventory across all warehouses."""
    product_totals: List[InventoryReportItem]
    low_stock_items: List[InventoryReportItem]
    generated_at: datetime

    @property
    def total_products(self) -> int:
        return len(self.product_totals)

    @property
    def total_quantity(self) -> int:
        return sum(item.quantity for item in self.product_totals)

    @property
    def total_value(self) -> Optional[float]:
        values = [item.total_value for item in self.product_totals if item.total_value is not None]
        return sum(values) if values else None