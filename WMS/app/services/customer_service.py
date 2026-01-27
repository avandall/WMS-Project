from typing import List, Optional
from app.repositories.interfaces.interfaces import ICustomerRepo


class CustomerService:
    def __init__(self, customer_repo: ICustomerRepo):
        self.customer_repo = customer_repo

    def create(self, data: dict):
        return self.customer_repo.create(data)

    def list(self):
        customers = self.customer_repo.get_all()
        result = []
        for c in customers:
            purchase_stats = self._purchase_stats(c.customer_id)
            result.append({
                "customer_id": c.customer_id,
                "name": c.name,
                "email": c.email,
                "phone": c.phone,
                "address": c.address,
                "debt_balance": c.debt_balance or 0.0,
                "created_at": c.created_at,
                **purchase_stats,
            })
        return result

    def get(self, customer_id: int):
        c = self.customer_repo.get(customer_id)
        if not c:
            return None
        purchases = self.customer_repo.list_purchases(customer_id)
        stats = self._purchase_stats(customer_id)
        return {
            "customer_id": c.customer_id,
            "name": c.name,
            "email": c.email,
            "phone": c.phone,
            "address": c.address,
            "debt_balance": c.debt_balance or 0.0,
            "created_at": c.created_at,
            "purchases": purchases,
            **stats,
        }

    def update_debt(self, customer_id: int, delta: float):
        self.customer_repo.update_debt(customer_id, delta)

    def record_purchase(self, customer_id: int, document_id: int, total_value: float):
        self.customer_repo.record_purchase(customer_id, document_id, total_value)

    def purchases(self, customer_id: int):
        return self.customer_repo.list_purchases(customer_id)

    def _purchase_stats(self, customer_id: int):
        purchases = self.customer_repo.list_purchases(customer_id)
        total = sum(p.get("total_value", 0) for p in purchases)
        return {"purchase_count": len(purchases), "total_purchased": total}
