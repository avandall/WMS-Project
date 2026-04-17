import asyncio
import random
from datetime import datetime
from sqlalchemy import select, text
from app.core.database import SessionLocal
from app.core.auth import hash_password

# Import toàn bộ model để SQLAlchemy không bị lỗi Relationship
from app.infrastructure.persistence.models.user_table import UserModel
from app.infrastructure.persistence.models.warehouse_table import WarehouseModel, WarehouseInventoryModel
from app.infrastructure.persistence.models.product_table import ProductModel
from app.infrastructure.persistence.models.customer_table import CustomerModel
from app.infrastructure.persistence.models.document_table import DocumentModel
from app.infrastructure.persistence.models.document_item_table import DocumentItemModel
from app.infrastructure.persistence.models.position_table import PositionModel
from app.infrastructure.persistence.models.inventory_table import InventoryModel
from app.infrastructure.persistence.models import *

from faker import Faker
fake = Faker(['vi_VN'])

async def reset_sequences(db):
    """Sửa lỗi UniqueViolation bằng cách reset bộ đếm ID của Postgres"""
    tables_pks = {
        'users': 'user_id',
        'warehouses': 'warehouse_id',
        'products': 'product_id',
        'customers': 'customer_id',
        'documents': 'document_id',
        'positions': 'id',
        'inventory': 'product_id'
    }
    for table, pk in tables_pks.items():
        try:
            db.execute(text(f"SELECT setval(pg_get_serial_sequence('{table}', '{pk}'), coalesce(max({pk}), 1), max({pk}) IS NOT NULL) FROM {table};"))
        except Exception:
            continue
    db.commit()

async def seed_everything():
    db = SessionLocal()
    print("🏗️  Bắt đầu nạp dữ liệu tổng hợp (Users + RAG)...")
    
    try:
        # 1. Reset ID tự tăng trước khi làm bất cứ việc gì
        await reset_sequences(db)

        # 2. TẠO NHIỀU USERS (Admin, Manager, Staff)
        print("👥 Đang tạo danh sách nhân sự...")
        roles = [
            ("admin@wms.com", "admin", "Hệ Thống Admin"),
            ("manager@wms.com", "manager", "Quản Lý Kho"),
            ("staff_hanoi@wms.com", "staff", "NV Kho Hà Nội"),
            ("staff_sg@wms.com", "staff", "NV Kho Sài Gòn")
        ]
        for email, role, name in roles:
            existing = db.execute(select(UserModel).where(UserModel.email == email)).scalar_one_or_none()
            if not existing:
                db.add(UserModel(
                    email=email,
                    hashed_password=hash_password("Admin123!"),
                    role=role,
                    full_name=name,
                    is_active=1
                ))
        db.flush()

        # 3. TẠO KHO VÀ VỊ TRÍ (Tránh lỗi Warehouse ID = None)
        print("📍 Đang tạo kho bãi và vị trí...")
        locations = ["Kho Hà Nội", "Kho Sài Gòn"]
        warehouses = []
        for loc in locations:
            wh = db.execute(select(WarehouseModel).where(WarehouseModel.location == loc)).scalar_one_or_none()
            if not wh:
                wh = WarehouseModel(location=loc)
                db.add(wh)
                db.flush()
            warehouses.append(wh)
            
            # Tạo vị trí (Position) cho mỗi kho
            for i in range(1, 4):
                pos_code = f"{loc[4:6].upper()}-A{i}"
                existing_pos = db.execute(select(PositionModel).where(PositionModel.code == pos_code)).first()
                if not existing_pos:
                    db.add(PositionModel(warehouse_id=wh.warehouse_id, code=pos_code, type="STORAGE"))
        db.flush()

        # 4. TẠO KHÁCH HÀNG & SẢN PHẨM (Dữ liệu cho AI RAG)
        print("📦 Đang tạo 50 sản phẩm mẫu...")
        products = []
        for i in range(50):
            p_id = 8000 + i
            p = ProductModel(
                product_id=p_id,
                name=f"Vật liệu {fake.word().upper()}-{random.randint(10,99)}",
                description=f"Dòng sản phẩm {fake.bs()}. Tiêu chuẩn {random.choice(['ISO', 'HACCP'])}.",
                price=random.uniform(50000, 2000000)
            )
            db.add(p)
            products.append(p)
        db.flush()

        # 5. TẠO CHỨNG TỪ (Fix lỗi Fail to Load do thiếu Warehouse)
        print("📄 Đang tạo chứng từ nhập xuất...")
        for _ in range(20):
            doc_type = random.choice(["IMPORT", "EXPORT"])
            wh = random.choice(warehouses)
            
            doc = DocumentModel(
                doc_type=doc_type,
                status="POSTED",
                created_by="admin@wms.com",
                from_warehouse_id=wh.warehouse_id if doc_type == "EXPORT" else None,
                to_warehouse_id=wh.warehouse_id if doc_type == "IMPORT" else None,
                created_at=datetime.now()
            )
            db.add(doc)
            db.flush()
            
            # Mỗi chứng từ nạp 2 sản phẩm ngẫu nhiên
            for p in random.sample(products, 2):
                db.add(DocumentItemModel(
                    document_id=doc.document_id,
                    product_id=p.product_id,
                    quantity=random.randint(10, 50),
                    unit_price=p.price
                ))

        db.commit()
        print("✨ HOÀN THÀNH! Dữ liệu đã sạch và sẵn sàng cho AI.")

    except Exception as e:
        print(f"❌ Lỗi: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(seed_everything())