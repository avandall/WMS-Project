from abc import ABC, abstractmethod
from typing import Any, Optional, List
from app.models.product_domain import Product
from app.models.warehouse_domain import Warehouse
from app.models.inventory_domain import InventoryItem
from app.models.document_domain import Document, DocumentType, DocumentStatus, DocumentProduct

class IProductRepo(ABC):
    @abstractmethod
    def save(self, product: Product) -> None:
        pass

    @abstractmethod
    def get(self, product_id: int) -> Optional[Product]:
        pass

    @abstractmethod
    def get_price(self, product_id: int) -> float:
        pass

    @abstractmethod
    def delete(self, product_id: int) -> None:
        pass

    @abstractmethod
    def create_product(self, product_id: int, name: str, price: float, description: str = None) -> Product:
        pass

    @abstractmethod
    def get_product_details(self, product_id: int) -> Product:
        pass

    @abstractmethod
    def update_product(self, product_id: int, name: str = None, price: float = None, description: str = None) -> Product:
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
    def delete(self, warehouse_id: int) -> None:
        pass

    @abstractmethod
    def add_product_to_warehouse(self, warehouse_id: int, product_id: int, quantity: int) -> None:
        pass

    @abstractmethod
    def remove_product_from_warehouse(self, warehouse_id: int, product_id: int, quantity: int) -> None:
        pass

    @abstractmethod
    def get_warehouse_inventory(self, warehouse_id: int) -> List[InventoryItem]:
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

    @abstractmethod
    def create_import_document(self, document_id: int, to_warehouse_id: int, items: List[DocumentProduct], created_by: str, note: str = None) -> Document:
        pass

    @abstractmethod
    def create_export_document(self, document_id: int, from_warehouse_id: int, items: List[DocumentProduct], created_by: str, note: str = None) -> Document:
        pass

    @abstractmethod
    def create_transfer_document(self, document_id: int, from_warehouse_id: int, to_warehouse_id: int, items: List[DocumentProduct], created_by: str, note: str = None) -> Document:
        pass

    @abstractmethod
    def get_document(self, document_id: int) -> Document:
        pass