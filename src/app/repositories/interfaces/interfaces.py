from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from app.models.product_domain import Product
from app.models.warehouse_domain import Warehouse
from app.models.inventory_domain import InventoryItem
from app.models.document_domain import Document, DocumentStatus
from app.models.user_domain import User
from app.models import document_domain
from app.models.position_domain import Position, PositionInventoryItem


class IProductRepo(ABC):
    @abstractmethod
    def save(self, product: Product) -> None:
        pass

    @abstractmethod
    def get(self, product_id: int) -> Optional[Product]:
        pass

    @abstractmethod
    def get_all(self) -> Dict[int, Product]:
        pass

    @abstractmethod
    def get_price(self, product_id: int) -> float:
        pass

    @abstractmethod
    def delete(self, product_id: int) -> None:
        pass


class IWarehouseRepo(ABC):
    @abstractmethod
    def create_warehouse(self, warehouse: Warehouse) -> None:
        pass

    @abstractmethod
    def save(self, warehouse: Warehouse) -> None:
        pass

    @abstractmethod
    def get(self, warehouse_id: int) -> Optional[Warehouse]:
        pass

    @abstractmethod
    def get_all(self) -> Dict[int, Warehouse]:
        pass

    @abstractmethod
    def delete(self, warehouse_id: int) -> None:
        pass

    @abstractmethod
    def get_warehouse_inventory(self, warehouse_id: int) -> List[InventoryItem]:
        pass

    @abstractmethod
    def add_product_to_warehouse(
        self, warehouse_id: int, product_id: int, quantity: int
    ) -> None:
        pass

    @abstractmethod
    def remove_product_from_warehouse(
        self, warehouse_id: int, product_id: int, quantity: int
    ) -> None:
        pass


class IInventoryRepo(ABC):
    @abstractmethod
    def save(self, inventory_item: InventoryItem) -> None:
        pass

    @abstractmethod
    def add_quantity(self, product_id: int, quantity: int) -> None:
        pass

    @abstractmethod
    def get_quantity(self, product_id: int) -> int:
        pass

    @abstractmethod
    def get_all(self) -> List[InventoryItem]:
        pass

    @abstractmethod
    def delete(self, product_id: int) -> None:
        pass

    @abstractmethod
    def remove_quantity(self, product_id: int, quantity: int) -> None:
        pass


class IDocumentRepo(ABC):
    @abstractmethod
    def save(self, document: Document) -> None:
        pass

    @abstractmethod
    def get(self, document_id: int) -> Optional[Document]:
        pass

    @abstractmethod
    def get_all(self) -> List[Document]:
        pass

    @abstractmethod
    def update_status(self, document_id: int, new_status: DocumentStatus) -> None:
        pass

    @abstractmethod
    def delete(self, document_id: int) -> None:
        pass


class IUserRepo(ABC):
    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def get(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def get_all(self) -> Dict[int, User]:
        pass


class ICustomerRepo(ABC):
    @abstractmethod
    def create(self, data: dict):
        pass

    @abstractmethod
    def get(self, customer_id: int):
        pass

    @abstractmethod
    def get_all(self) -> List[dict]:
        pass

    @abstractmethod
    def update_debt(self, customer_id: int, delta: float) -> None:
        pass

    @abstractmethod
    def record_purchase(self, customer_id: int, document_id: int, total_value: float) -> None:
        pass

    @abstractmethod
    def list_purchases(self, customer_id: int) -> List[dict]:
        pass


class IPositionRepo(ABC):
    @abstractmethod
    def ensure_default_positions(self, warehouse_id: int) -> None:
        pass

    @abstractmethod
    def create_position(
        self,
        *,
        warehouse_id: int,
        code: str,
        type: str = "STORAGE",
        description: Optional[str] = None,
    ) -> Position:
        pass

    @abstractmethod
    def list_positions(
        self, warehouse_id: int, *, include_inactive: bool = False
    ) -> List[Position]:
        pass

    @abstractmethod
    def get_position(self, warehouse_id: int, code: str) -> Position:
        pass

    @abstractmethod
    def list_position_inventory(
        self, warehouse_id: int, code: str
    ) -> List[PositionInventoryItem]:
        pass

    @abstractmethod
    def get_position_model(self, warehouse_id: int, code: str):
        """Internal helper for services needing DB identity (position id)."""
        pass

    @abstractmethod
    def get_total_quantity_for_product(self, warehouse_id: int, product_id: int) -> int:
        pass

    @abstractmethod
    def adjust_position_stock(self, *, position_id: int, product_id: int, delta: int) -> None:
        pass

    @abstractmethod
    def allocate_and_remove(
        self,
        *,
        warehouse_id: int,
        product_id: int,
        quantity: int,
        preferred_position_codes: Optional[List[str]] = None,
    ):
        pass


class IAuditEventRepo(ABC):
    @abstractmethod
    def create_event(
        self,
        *,
        action: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        warehouse_id: Optional[int] = None,
        payload: Optional[dict[str, Any]] = None,
        user_id: Optional[int] = None,
    ) -> int:
        pass
