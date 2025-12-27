"""
Value Objects for PMKT Warehouse Management System.
Value objects are immutable objects that represent concepts in the domain.
"""

from typing import Any
from decimal import Decimal, ROUND_HALF_UP


class Money:
    """
    Value object representing monetary amounts.
    Ensures consistent handling of currency and precision.
    """

    def __init__(self, amount: float | int | str | Decimal):
        self._amount = Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if self._amount < 0:
            raise ValueError("Money amount cannot be negative")

    @property
    def amount(self) -> Decimal:
        return self._amount

    def __add__(self, other: 'Money') -> 'Money':
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self._amount + other._amount)

    def __sub__(self, other: 'Money') -> 'Money':
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self._amount - other._amount)

    def __mul__(self, other: int | float | Decimal) -> 'Money':
        return Money(self._amount * Decimal(str(other)))

    def __truediv__(self, other: int | float | Decimal) -> 'Money':
        return Money(self._amount / Decimal(str(other)))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self._amount == other._amount

    def __lt__(self, other: 'Money') -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self._amount < other._amount

    def __le__(self, other: 'Money') -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self._amount <= other._amount

    def __gt__(self, other: 'Money') -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self._amount > other._amount

    def __ge__(self, other: 'Money') -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self._amount >= other._amount

    def __str__(self) -> str:
        return f"${self._amount}"

    def __repr__(self) -> str:
        return f"Money({self._amount})"

    def to_float(self) -> float:
        return float(self._amount)

    def to_decimal(self) -> Decimal:
        return self._amount


class Quantity:
    """
    Value object representing quantities.
    Ensures non-negative integer quantities.
    """

    def __init__(self, value: int):
        if not isinstance(value, int):
            raise TypeError("Quantity must be an integer")
        if value < 0:
            raise ValueError("Quantity cannot be negative")
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    def __add__(self, other: 'Quantity') -> 'Quantity':
        if not isinstance(other, Quantity):
            return NotImplemented
        return Quantity(self._value + other._value)

    def __sub__(self, other: 'Quantity') -> 'Quantity':
        if not isinstance(other, Quantity):
            return NotImplemented
        if other._value > self._value:
            raise ValueError("Cannot subtract larger quantity from smaller")
        return Quantity(self._value - other._value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Quantity):
            return NotImplemented
        return self._value == other._value

    def __lt__(self, other: 'Quantity') -> bool:
        if not isinstance(other, Quantity):
            return NotImplemented
        return self._value < other._value

    def __le__(self, other: 'Quantity') -> bool:
        if not isinstance(other, Quantity):
            return NotImplemented
        return self._value <= other._value

    def __gt__(self, other: 'Quantity') -> bool:
        if not isinstance(other, Quantity):
            return NotImplemented
        return self._value > other._value

    def __ge__(self, other: 'Quantity') -> bool:
        if not isinstance(other, Quantity):
            return NotImplemented
        return self._value >= other._value

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return f"Quantity({self._value})"


class ProductId:
    """
    Value object for Product ID.
    Ensures valid product identifiers.
    """

    def __init__(self, value: int):
        if not isinstance(value, int):
            raise TypeError("Product ID must be an integer")
        if value <= 0:
            raise ValueError("Product ID must be positive")
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProductId):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return f"ProductId({self._value})"


class WarehouseId:
    """
    Value object for Warehouse ID.
    Ensures valid warehouse identifiers.
    """

    def __init__(self, value: int):
        if not isinstance(value, int):
            raise TypeError("Warehouse ID must be an integer")
        if value <= 0:
            raise ValueError("Warehouse ID must be positive")
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WarehouseId):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return f"WarehouseId({self._value})"