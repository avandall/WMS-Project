"""
Product Report classes for PMKT Warehouse Management System.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from dataclasses import dataclass

@dataclass
class ProductMovementItem:
    """Represents a product movement in report."""
    document_id: int
    doc_type: str
    status: str
    date: str
    quantity: int
    unit_price: float
    total_value: float
    from_warehouse: Optional[str]
    to_warehouse: Optional[str]

@dataclass
class ProductMovementReport:
    """Product movement report."""
    product_id: int
    product_name: str
    filters: Dict[str, Any]
    movements: List[ProductMovementItem]
    generated_at: datetime

    @property
    def total_movements(self) -> int:
        return len(self.movements)

    @property
    def total_quantity_moved(self) -> int:
        return sum(movement.quantity for movement in self.movements)

    @property
    def total_value(self) -> float:
        return sum(movement.total_value for movement in self.movements)