import asyncio
import random
from datetime import datetime
from sqlalchemy import select, text
from app.core.database import SessionLocal
from app.core.auth import hash_password

# Import toàn bộ model để tránh lỗi Relationship
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
    """Sửa lỗi trùng ID bằng cách đặt lại bộ đếm của Postgres"""
    print("🔄 Resetting database sequences...")
    tables_pks = {
        'users': 'user_id',
        'warehouses': 'warehouse_id',
        'products': 'product_id',
        'customers': 'customer_id',
        'documents': 'document_id',
        'positions': 'id'
    }
    for table, pk in tables_pks.items():
        try:
            db.execute(text(f"SELECT setval(pg_get_serial_sequence('{table}', '{pk}'), coalesce(max({pk}), 1), max({pk}) IS NOT NULL) FROM {table};"))
        except Exception as e:
            print(f"⚠️ Skip reset for {table}: {e}")
    db.commit()

async def seed_everything():
    db = SessionLocal()
    print("🏗️  Bắt đầu nạp dữ liệu WMS v3 (Fixed Roles + Customers)...")
    
    try:
        # 1. Reset ID
        await reset_sequences(db)

        # 2. TẠO USERS (Sử dụng đúng Role hệ thống cho phép)
        print("👥 Creating users with valid roles...")
        valid_users = [
            ("admin@wms.com", "admin", "Hệ Thống Admin"),
            ("ketoan@wms.com", "accountant", "Kế Toán Trưởng"),
            ("banhang@wms.com", "sales", "Trưởng Phòng Kinh Doanh"),
            ("thukho@wms.com", "warehouse", "Thủ Kho Tổng"),
            ("khach@wms.com", "user", "Người Dùng Phụ")
        ]
        for email, role, name in valid_users:
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

        # 3. TẠO KHÁCH HÀNG (Dữ liệu mới yêu cầu)
        print("👥 Creating 20 sample customers...")
        customers = []
        for _ in range(20):
            cust = CustomerModel(
                name=fake.name(),
                email=fake.email(),
                phone=fake.phone_number(),
                address=fake.address(),
                debt_balance=random.uniform(0, 5000000)
            )
            db.add(cust)
            customers.append(cust)
        db.flush()

        # 4. TẠO KHO
        print("📍 Creating warehouses...")
        warehouses = []
        for loc_name in ["Kho Miền Bắc", "Kho Miền Nam", "Kho Miền Trung", "Kho Miền Tây"]:
            wh = db.execute(select(WarehouseModel).where(WarehouseModel.location == loc_name)).scalar_one_or_none()
            if not wh:
                wh = WarehouseModel(location=loc_name)
                db.add(wh)
                db.flush()
            warehouses.append(wh)

        # 5. TẠO SẢN PHẨM RAG (Metadata phong phú)
        print("📦 Creating realistic products for AI RAG...")
        # Danh sách sản phẩm thực tế theo ngành hàng
        sample_data = [
            {"cat": "Điện tử", "items": ["Máy hàn thiếc Quick 936A", "Đồng hồ vạn năng Fluke", "Kính hiển vi soi mạch", "Bo mạch chủ Asus H510"]},
            {"cat": "Cơ khí", "items": ["Máy mài cầm tay Bosch", "Bộ cờ lê vòng miệng", "Thước kẹp điện tử Mitutoyo", "Mũi khoan bê tông"]},
            {"cat": "Gỗ", "items": ["Máy bào gỗ Makita", "Keo dán gỗ chuyên dụng", "Bộ đục gỗ cầm tay", "Gỗ thông tấm nhập khẩu"]},
            {"cat": "Vật liệu may", "items": ["Cuộn vải thun Cotton", "Chỉ may công nghiệp", "Khóa kéo YKK", "Phấn may cao cấp"]}
        ]

        products = []
        p_id_counter = 6000
        for entry in sample_data:
            cat = entry["cat"]
            for item_name in entry["items"]:
                p = ProductModel(
                    product_id=p_id_counter,
                    name=item_name,
                    description=f"Sản phẩm thuộc nhóm {cat}. Chất lượng đạt chuẩn {random.choice(['ISO 9001', 'TCCS', 'Japan Standard'])}. Ứng dụng rộng rãi trong sản xuất {cat.lower()}.",
                    price=random.uniform(200000, 5000000)
                )
                db.add(p)
                products.append(p)
                p_id_counter += 1
        db.flush()

        # 6. TẠO TỒN KHO (Inventory & Warehouse Inventory)
        print("📊 Adding stock levels to inventory...")
        for p in products:
            # A. Tồn kho tổng (Bảng inventory)
            total_qty = random.randint(100, 500)
            inv = InventoryModel(
                product_id=p.product_id,
                quantity=total_qty
            )
            db.add(inv)

            # B. Phân bổ tồn kho vào các kho cụ thể (Bảng warehouse_inventory)
            # Giả sử chia hàng vào 2 kho hiện có
            for wh in warehouses:
                share_qty = total_qty // len(warehouses) # Chia đều hoặc random
                wh_inv = WarehouseInventoryModel(
                    warehouse_id=wh.warehouse_id,
                    product_id=p.product_id,
                    quantity=share_qty
                )
                db.add(wh_inv)
                
        db.flush()
        print(f"✅ Added {len(products)} products with stock levels.")

        # 7. TẠO CHỨNG TỪ (Đảm bảo có Warehouse và Customer)
        print("📄 Creating documents with full links...")
        for i in range(15):
            doc_type = "IMPORT" if i % 2 == 0 else "EXPORT"
            wh = random.choice(warehouses)
            cust = random.choice(customers)
            
            doc = DocumentModel(
                doc_type=doc_type,
                status="POSTED",
                created_by="admin@wms.com",
                from_warehouse_id=wh.warehouse_id if doc_type == "EXPORT" else None,
                to_warehouse_id=wh.warehouse_id if doc_type == "IMPORT" else None,
                customer_id=cust.customer_id,
                created_at=datetime.now()
            )
            db.add(doc)
            db.flush()
            
            # Thêm sản phẩm vào chứng từ
            selected_products = random.sample(products, 2)
            for p in selected_products:
                db.add(DocumentItemModel(
                    document_id=doc.document_id,
                    product_id=p.product_id,
                    quantity=random.randint(1, 100),
                    unit_price=p.price
                ))

        db.commit()
        print("✨ SEED COMPLETED: Fixed Roles, Added Customers, and Linked Warehouses!")

    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(seed_everything())