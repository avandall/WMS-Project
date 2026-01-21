"""
SQLAlchemy models for PMKT Warehouse Management System with PostgreSQL.
Includes production-grade indexes and constraints.
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
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProductModel(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)  # Index for searching
    description = Column(String(500))
    price = Column(Float, nullable=False, default=0.0)
    
    __table_args__ = (
        CheckConstraint('price >= 0', name='check_product_price_positive'),
        Index('ix_products_name', 'name'),  # Explicit index for name searches
    )

    inventory = relationship(
        "InventoryModel",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan",
    )
    warehouse_items = relationship("WarehouseInventoryModel", back_populates="product")
    document_items = relationship("DocumentItemModel", back_populates="product")


class WarehouseModel(Base):
    __tablename__ = "warehouses"

    warehouse_id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String(200), nullable=False, unique=True, index=True)

    inventory_items = relationship(
        "WarehouseInventoryModel",
        back_populates="warehouse",
        cascade="all, delete-orphan",
    )


class InventoryModel(Base):
    __tablename__ = "inventory"

    product_id = Column(Integer, ForeignKey("products.product_id"), primary_key=True)
    quantity = Column(Integer, nullable=False, default=0)
    
    __table_args__ = (
        CheckConstraint('quantity >= 0', name='check_inventory_quantity_positive'),
    )

    product = relationship("ProductModel", back_populates="inventory")


class WarehouseInventoryModel(Base):
    __tablename__ = "warehouse_inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column(
        Integer, ForeignKey("warehouses.warehouse_id"), nullable=False, index=True
    )
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("warehouse_id", "product_id", name="uq_warehouse_product"),
        CheckConstraint('quantity >= 0', name='check_warehouse_inventory_quantity_positive'),
        Index('ix_warehouse_inventory_warehouse_product', 'warehouse_id', 'product_id'),
    )

    warehouse = relationship("WarehouseModel", back_populates="inventory_items")
    product = relationship("ProductModel", back_populates="warehouse_items")


class DocumentModel(Base):
    __tablename__ = "documents"

    document_id = Column(Integer, primary_key=True, autoincrement=True)
    doc_type = Column(String(20), nullable=False, index=True)  # Index for filtering by type
    status = Column(String(20), nullable=False, index=True)  # Index for filtering by status
    from_warehouse_id = Column(
        Integer, ForeignKey("warehouses.warehouse_id"), nullable=True, index=True
    )
    to_warehouse_id = Column(
        Integer, ForeignKey("warehouses.warehouse_id"), nullable=True, index=True
    )
    created_by = Column(String(100), nullable=False, index=True)
    approved_by = Column(String(100))
    note = Column(String(500))
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)  # Index for date queries
    posted_at = Column(DateTime, index=True)
    cancelled_at = Column(DateTime)
    cancellation_reason = Column(String(500))
    
    __table_args__ = (
        # Composite indexes for common query patterns
        Index('ix_documents_status_created_at', 'status', 'created_at'),
        Index('ix_documents_type_status', 'doc_type', 'status'),
        Index('ix_documents_created_by_created_at', 'created_by', 'created_at'),
    )

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
