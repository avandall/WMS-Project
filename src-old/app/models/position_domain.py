"""
Position (bin/location) domain logic for PMKT Warehouse Management System.
Tracks where stock is stored inside each warehouse.
"""

from dataclasses import dataclass

from app.exceptions.business_exceptions import ValidationError


@dataclass(frozen=True)
class Position:
    id: int
    warehouse_id: int
    code: str
    type: str
    description: str | None = None
    is_active: bool = True

    def __post_init__(self) -> None:
        if self.warehouse_id <= 0:
            raise ValidationError("warehouse_id must be positive")
        if not self.code or not self.code.strip():
            raise ValidationError("position code is required")
        if len(self.code) > 50:
            raise ValidationError("position code too long (max 50)")
        if not self.type or not self.type.strip():
            raise ValidationError("position type is required")
        if len(self.type) > 20:
            raise ValidationError("position type too long (max 20)")


@dataclass(frozen=True)
class PositionInventoryItem:
    warehouse_id: int
    position_code: str
    product_id: int
    quantity: int

