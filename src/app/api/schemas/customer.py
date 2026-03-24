from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class CustomerResponse(BaseModel):
    customer_id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    debt_balance: float
    created_at: datetime
    purchase_count: int = 0
    total_purchased: float = 0.0


class DebtUpdate(BaseModel):
    amount: float = Field(..., description="Positive to increase debt, negative to reduce (payment)")


class PurchaseResponse(BaseModel):
    document_id: int
    total_value: float
    created_at: datetime


class CustomerDetailResponse(CustomerResponse):
    purchases: List[PurchaseResponse] = []
