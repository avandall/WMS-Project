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


class UserModel(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user", index=True)
    full_name = Column(String(255))
    is_active = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)

    audit_logs = relationship("AuditLogModel", back_populates="user")


class ProductModel(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # Index defined in __table_args__
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
    doc_type = Column(String(20), nullable=False)  # Index in composite
    status = Column(String(20), nullable=False)  # Index in composite
    from_warehouse_id = Column(
        Integer, ForeignKey("warehouses.warehouse_id"), nullable=True, index=True
    )
    to_warehouse_id = Column(
        Integer, ForeignKey("warehouses.warehouse_id"), nullable=True, index=True
    )
    created_by = Column(String(100), nullable=False)  # Index in composite
    approved_by = Column(String(100))
    note = Column(String(500))
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)  # Index in composite
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


class CustomerModel(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(String(255))
    debt_balance = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)

    purchases = relationship("CustomerPurchaseModel", back_populates="customer")


class CustomerPurchaseModel(Base):
    __tablename__ = "customer_purchases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("documents.document_id"), nullable=False, index=True)
    total_value = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)

    customer = relationship("CustomerModel", back_populates="purchases")


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True, index=True)
    path = Column(String(500), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    client_ip = Column(String(100))
    user_agent = Column(String(300))
    latency_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)

    user = relationship("UserModel", back_populates="audit_logs")

    __table_args__ = (
        Index("ix_audit_logs_user_path", "user_id", "path"),
        Index("ix_audit_logs_created", "created_at"),
    )
