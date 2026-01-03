"""
SQLAlchemy models for PMKT Warehouse Management System with PostgreSQL.
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProductModel(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False, default=0.0)

    inventory = relationship(
        "InventoryModel", back_populates="product", uselist=False, cascade="all, delete-orphan"
    )
    warehouse_items = relationship("WarehouseInventoryModel", back_populates="product")
    document_items = relationship("DocumentItemModel", back_populates="product")


class WarehouseModel(Base):
    __tablename__ = "warehouses"

    warehouse_id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String(200), nullable=False, unique=True)

    inventory_items = relationship(
        "WarehouseInventoryModel",
        back_populates="warehouse",
        cascade="all, delete-orphan",
    )


class InventoryModel(Base):
    __tablename__ = "inventory"

    product_id = Column(Integer, ForeignKey("products.product_id"), primary_key=True)
    quantity = Column(Integer, nullable=False, default=0)

    product = relationship("ProductModel", back_populates="inventory")


class WarehouseInventoryModel(Base):
    __tablename__ = "warehouse_inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.warehouse_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)

    __table_args__ = (UniqueConstraint("warehouse_id", "product_id", name="uq_warehouse_product"),)

    warehouse = relationship("WarehouseModel", back_populates="inventory_items")
    product = relationship("ProductModel", back_populates="warehouse_items")


class DocumentModel(Base):
    __tablename__ = "documents"

    document_id = Column(Integer, primary_key=True, autoincrement=True)
    doc_type = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    from_warehouse_id = Column(Integer, ForeignKey("warehouses.warehouse_id"), nullable=True)
    to_warehouse_id = Column(Integer, ForeignKey("warehouses.warehouse_id"), nullable=True)
    created_by = Column(String(100), nullable=False)
    approved_by = Column(String(100))
    note = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    posted_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    cancellation_reason = Column(String(500))

    items = relationship(
        "DocumentItemModel",
        back_populates="document",
        cascade="all, delete-orphan",
    )


class DocumentItemModel(Base):
    __tablename__ = "document_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.document_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    document = relationship("DocumentModel", back_populates="items")
    product = relationship("ProductModel", back_populates="document_items")
