"""
Warehouse Report classes for PMKT Warehouse Management System.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

@dataclass
class WarehousePerformanceItem:
    """Represents a warehouse in performance report."""
    warehouse_id: int
    location: str
    item_count: int
    total_quantity: int
    total_value: Optional[float]

@dataclass
class WarehousePerformanceReport:
    """Warehouse performance report."""
    warehouses: List[WarehousePerformanceItem]
    generated_at: datetime

    @property
    def total_warehouses(self) -> int:
        return len(self.warehouses)

    @property
    def total_value(self) -> Optional[float]:
        values = [w.total_value for w in self.warehouses if w.total_value is not None]
        return sum(values) if values else None