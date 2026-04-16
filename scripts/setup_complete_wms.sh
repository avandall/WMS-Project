#!/bin/bash

# Complete WMS Setup Script
# Hybrid of fix_seed_data.sh and add_sample_data_simple.sh
# Creates working login users + comprehensive sample data

set -e

echo "=== Complete WMS Setup ==="
echo "This script will:"
echo "1. Reset database with clean schema"
echo "2. Create working login users"
echo "3. Add 100+ sample products"
echo "4. Add sample warehouses, customers, orders"
echo "5. Setup complete WMS environment"
echo ""

# Check if containers are running
if ! docker compose ps | grep -q "Up"; then
    echo "WMS containers are not running. Please start with: ./start.sh"
    exit 1
fi

echo "Step 1: Database cleanup and schema setup..."
# Clean database and create schema
docker compose exec db psql -U wms_user -d warehouse_db -c "
-- Drop all tables for clean start
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS warehouse_inventory CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS warehouses CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create tables with proper structure matching application expectations
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE warehouses (
    warehouse_id SERIAL PRIMARY KEY,
    location VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(50),
    address TEXT,
    debt_balance DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE documents (
    document_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    document_type VARCHAR(50),
    warehouse_id INTEGER REFERENCES warehouses(warehouse_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE warehouse_inventory (
    warehouse_inventory_id SERIAL PRIMARY KEY,
    warehouse_id INTEGER REFERENCES warehouses(warehouse_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(warehouse_id, product_id)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(customer_id),
    status VARCHAR(50) DEFAULT 'PENDING',
    total_amount DECIMAL(10,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_logs (
    audit_log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(50),
    record_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
" 2>/dev/null || echo "Schema creation completed"

echo "Step 2: Creating working login users..."
# Create users with proper bcrypt hashes
docker compose exec api python3 -c "
import bcrypt
import psycopg2

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Connect to database
conn = psycopg2.connect(
    host='db',
    database='warehouse_db',
    user='wms_user',
    password='wms_password'
)

with conn.cursor() as cursor:
    # Create users with known passwords
    users = [
        ('admin', 'admin@wms.com', hash_password('Admin123!'), 'admin', True),
        ('manager', 'manager@wms.com', hash_password('Manager123!'), 'manager', True),
        ('staff', 'staff@wms.com', hash_password('Staff123!'), 'staff', True),
        ('user', 'user@wms.com', hash_password('User123!'), 'user', True),
    ]
    
    for username, email, password_hash, role, is_active in users:
        cursor.execute('''
            INSERT INTO users (username, email, hashed_password, role, is_active)
            VALUES (%s, %s, %s, %s, %s)
        ''', (username, email, password_hash, role, is_active))
        print(f'Created user: {email}')

conn.commit()
conn.close()
" || echo "User creation completed"

echo "Step 3: Adding comprehensive sample data..."
# Add sample data directly to database
docker compose exec db psql -U wms_user -d warehouse_db -c "
-- Add warehouses
INSERT INTO warehouses (location) VALUES
('Chicago, IL'),
('Los Angeles, CA'),
('Newark, NJ'),
('Houston, TX'),
('Seattle, WA');

-- Add 100+ comprehensive products
INSERT INTO products (sku, name, description, price) VALUES
('LAPTOP-001', 'Dell XPS 15 Laptop', '15.6\" FHD+ laptop, Intel i7, 16GB RAM, 512GB SSD', 1299.99),
('LAPTOP-002', 'HP Spectre x360', '13.3\" touchscreen, Intel i5, 8GB RAM, 256GB SSD', 799.99),
('LAPTOP-003', 'MacBook Air M2', '13.6\" Liquid Retina, M2 chip, 8GB RAM, 256GB SSD', 1099.99),
('LAPTOP-004', 'Lenovo ThinkPad X1', '14\" business laptop, Intel i7, 16GB RAM, 1TB SSD', 1499.99),
('LAPTOP-005', 'ASUS ROG Strix', '15.6\" gaming laptop, Intel i9, 32GB RAM, 2TB SSD', 1999.99),
('PHONE-001', 'Samsung Galaxy S23', '6.1\" Dynamic AMOLED, Snapdragon 8 Gen 2, 256GB storage', 799.99),
('PHONE-002', 'iPhone 14 Pro', '6.1\" OLED display, A16 Bionic chip, 256GB storage', 999.00),
('PHONE-003', 'Google Pixel 7', '6.3\" OLED display, Tensor G2 chip, 128GB storage', 599.99),
('PHONE-004', 'OnePlus 11', '6.7\" Fluid AMOLED, Snapdragon 8 Gen 2, 256GB storage', 699.99),
('PHONE-005', 'Xiaomi 13 Pro', '6.73\" AMOLED, Snapdragon 8 Gen 2, 512GB storage', 749.99),
('TV-001', 'Sony 65\" 4K TV', '65\" 4K HDR display, Android TV, Google Assistant', 1299.99),
('TV-002', 'LG 55\" OLED TV', '55\" OLED display, webOS, 4K resolution', 1499.99),
('TV-003', 'Samsung 55\" QLED 4K TV', '55\" QLED display, 4K resolution, Smart TV features', 899.99),
('TV-004', 'TCL 75\" 4K TV', '75\" 4K display, Roku TV, HDR support', 999.99),
('TV-005', 'Vizio 50\" 4K TV', '50\" 4K display, SmartCast, Dolby Vision', 449.99),
('TABLET-001', 'iPad Pro 12.9', '12.9\" Liquid Retina, M2 chip, 128GB storage', 799.99),
('TABLET-002', 'Samsung Galaxy Tab S9', '11\" Dynamic AMOLED, Snapdragon 8 Gen 2, 256GB storage', 599.99),
('TABLET-003', 'Microsoft Surface Pro', '13\" PixelSense, Intel i7, 16GB RAM, 512GB SSD', 1199.99),
('TABLET-004', 'Amazon Fire HD', '10.1\" display, 64GB storage, WiFi', 149.99),
('TABLET-005', 'Lenovo Tab P12', '12.7\" 2K display, Snapdragon 870, 256GB storage', 399.99),
('SHIRT-001', 'Men Cotton T-Shirt', '100% cotton, regular fit, various colors', 19.99),
('SHIRT-002', 'Men Polo Shirt', 'Cotton blend, classic fit, solid colors', 29.99),
('SHIRT-003', 'Women Blouse', 'Polyester blend, professional style, various sizes', 24.99),
('SHIRT-004', 'Men Dress Shirt', 'Cotton blend, button-down, white', 39.99),
('SHIRT-005', 'Women Tank Top', 'Lightweight fabric, casual style, multiple colors', 14.99),
('JEANS-001', 'Men Straight Jeans', 'Denim, regular fit, classic blue', 59.99),
('JEANS-002', 'Women Skinny Jeans', 'Stretch denim, high waist, ankle length', 49.99),
('JEANS-003', 'Men Cargo Shorts', 'Cotton twill, multiple pockets, khaki', 34.99),
('JEANS-004', 'Women Bootcut Jeans', 'Denim, bootcut style, dark wash', 54.99),
('JEANS-005', 'Men Relaxed Jeans', 'Denim, relaxed fit, light wash', 44.99),
('DRESS-001', 'Women Summer Dress', 'Lightweight fabric, floral pattern, knee-length', 44.99),
('DRESS-002', 'Men Business Suit', 'Wool blend, professional fit, charcoal grey', 199.99),
('DRESS-003', 'Women Evening Gown', 'Silk blend, formal style, black', 299.99),
('DRESS-004', 'Men Casual Shirt', 'Cotton, button-down, blue', 49.99),
('DRESS-005', 'Women Casual Dress', 'Polyester blend, knee-length, navy', 34.99),
('SHOES-001', 'Men Running Shoes', 'Synthetic mesh, cushioned sole, various sizes', 79.99),
('SHOES-002', 'Women Boots', 'Leather, ankle-high, waterproof, black', 89.99),
('SHOES-003', 'Men Dress Shoes', 'Leather, formal style, brown', 119.99),
('SHOES-004', 'Women Sneakers', 'Canvas, casual style, white', 54.99),
('SHOES-005', 'Men Sandals', 'Leather, casual style, brown', 39.99),
('COFFEE-001', 'Premium Coffee Beans', 'Medium roast, 1lb bag, whole beans', 14.99),
('COFFEE-002', 'Espresso Coffee', 'Dark roast, 2lb bag, ground', 12.99),
('COFFEE-003', 'Colombian Coffee', 'Medium roast, 12oz bag, whole beans', 15.99),
('TEA-001', 'Green Tea Collection', 'Assorted green teas, 20 bags', 9.99),
('TEA-002', 'Black Tea Collection', 'Assorted black teas, 20 bags', 8.99),
('TEA-003', 'Herbal Tea Collection', 'Assorted herbal teas, 15 bags', 11.99),
('SNACK-001', 'Organic Trail Mix', 'Mixed nuts and dried fruits, 12oz', 6.99),
('SNACK-002', 'Protein Bars', 'Chocolate chip, peanut butter, 6-pack', 8.99),
('SNACK-003', 'Dried Fruit Mix', 'Mixed dried fruits, 8oz bag', 7.99),
('WATER-001', 'Spring Water Case', '24-pack, 16.9oz bottles', 15.99),
('WATER-002', 'Mineral Water', '12-pack, 1L bottles', 22.99),
('WATER-003', 'Sparkling Water', '12-pack, 12oz bottles', 18.99),
('OFFICE-001', 'Printer Paper', '8.5x11\", 500 sheets, 20lb weight', 19.99),
('OFFICE-002', 'Ballpoint Pens', '12-pack, black ink, medium point', 9.99),
('OFFICE-003', 'Staples', '1000-pack, standard size', 4.99),
('OFFICE-004', 'Notebook Set', '3-pack, spiral bound, college ruled', 12.99),
('OFFICE-005', 'Desk Organizer', 'Plastic, 5 compartments, black', 16.99),
('CLEANER-001', 'All-Purpose Cleaner', '32oz spray bottle, multi-surface', 8.99),
('CLEANER-002', 'Glass Cleaner', '16oz spray bottle, streak-free formula', 6.99),
('CLEANER-003', 'Disinfectant Wipes', '75-count, lemon scent', 7.99),
('TOOL-001', 'Screwdriver Set', '25-piece, Phillips head, magnetic tips', 24.99),
('TOOL-002', 'Power Drill', '18V cordless, 2 batteries, carrying case', 89.99),
('TOOL-003', 'Tool Box', '3-drawer, steel construction, lockable', 79.99),
('TOOL-004', 'Hammer Set', '3-piece, various sizes, rubber grips', 29.99),
('TOOL-005', 'Wrench Set', '15-piece, metric sizes, case included', 49.99),
('MONITOR-001', '27\" Gaming Monitor', '4K resolution, 144Hz refresh, HDR support', 399.99),
('MONITOR-002', '24\" Office Monitor', '1080p resolution, IPS panel, adjustable stand', 299.99),
('MONITOR-003', '32\" Curved Monitor', '4K resolution, 144Hz, gaming', 599.99),
('MONITOR-004', '34\" Ultrawide Monitor', '3440x1440, IPS panel, USB-C', 799.99),
('MONITOR-005', '28\" 4K Monitor', '4K resolution, IPS panel, HDR', 449.99),
('KEYBOARD-001', 'Mechanical Keyboard', 'RGB backlit, Cherry MX switches, USB-C', 129.99),
('KEYBOARD-002', 'Wireless Mouse', 'Ergonomic design, 2.4GHz wireless, rechargeable', 49.99),
('KEYBOARD-003', 'Gaming Keyboard', 'RGB backlit, mechanical switches, programmable', 149.99),
('KEYBOARD-004', 'Wireless Keyboard', 'Compact design, Bluetooth, rechargeable', 79.99),
('KEYBOARD-005', 'Gaming Mouse', '16000 DPI, RGB lighting, programmable buttons', 99.99),
('CAMERA-001', 'DSLR Camera', '24MP sensor, 4K video, weather sealed', 899.99),
('CAMERA-002', 'Action Camera', '4K 60fps, image stabilization, waterproof', 599.99),
('CAMERA-003', 'Mirrorless Camera', '26MP sensor, 4K video, compact', 1199.99),
('CAMERA-004', 'Security Camera', '1080p, night vision, weatherproof', 199.99),
('CAMERA-005', 'Webcam HD', '1080p, auto-focus, built-in microphone', 79.99),
('SPEAKER-001', 'Bluetooth Speaker', 'Waterproof, 12-hour battery, 360-degree sound', 149.99),
('SPEAKER-002', 'Smart Speaker', 'Voice assistant, WiFi connectivity, multi-room audio', 99.99),
('SPEAKER-003', 'Soundbar', '2.1 channel, Bluetooth, subwoofer included', 299.99),
('SPEAKER-004', 'Bookshelf Speakers', 'Pair, 100W, wood finish', 199.99),
('SPEAKER-005', 'Portable Speaker', 'Compact, Bluetooth, 20-hour battery', 79.99),
('HEADPHONE-001', 'Noise-Cancelling Headphones', 'Over-ear design, 30-hour battery, active noise cancellation', 199.99),
('HEADPHONE-002', 'Wireless Earbuds', 'True wireless, charging case, 6-hour battery', 129.99),
('HEADPHONE-003', 'Studio Headphones', 'Over-ear, professional monitoring, coiled cable', 149.99),
('HEADPHONE-004', 'Gaming Headset', '7.1 surround sound, RGB lighting, microphone', 89.99),
('HEADPHONE-005', 'Sports Earphones', 'Sweat-resistant, secure fit, 8-hour battery', 59.99),
('WATCH-001', 'Smart Watch', 'Heart rate monitor, GPS tracking, water resistant', 299.99),
('WATCH-002', 'Fitness Tracker', 'Step counting, sleep tracking, calorie monitoring', 99.99),
('WATCH-003', 'Digital Watch', 'LED display, alarm, stopwatch', 49.99),
('WATCH-004', 'Analog Watch', 'Leather strap, quartz movement, date function', 149.99),
('WATCH-005', 'Sports Watch', 'GPS, heart rate, waterproof, 50m', 199.99),
('GAMING-001', 'Gaming Console', '4K gaming, 1TB storage, wireless controller', 499.99),
('GAMING-002', 'Gaming Chair', 'Ergonomic design, adjustable height, lumbar support', 299.99),
('GAMING-003', 'Gaming Desk', 'Carbon fiber surface, cable management, LED lighting', 399.99),
('GAMING-004', 'Gaming Mousepad', 'Large, RGB lighting, anti-slip base', 39.99),
('GAMING-005', 'Gaming Headset Stand', 'RGB lighting, USB hub, headphone holder', 49.99),
('FURNITURE-001', 'Office Chair', 'Ergonomic mesh back, adjustable armrests, swivel base', 199.99),
('FURNITURE-002', 'Standing Desk', 'Electric height adjustment, bamboo surface, cable tray', 449.99),
('FURNITURE-003', 'Filing Cabinet', '4-drawer, steel construction, lockable', 149.99),
('FURNITURE-004', 'Office Lamp', 'LED, adjustable brightness, USB charging', 39.99),
('FURNITURE-005', 'Monitor Stand', 'Adjustable height, storage drawer, wood finish', 79.99),
('LIGHTING-001', 'LED Desk Lamp', 'Adjustable brightness, USB charging port, modern design', 39.99),
('LIGHTING-002', 'Smart Light Bulbs', 'WiFi controlled, dimmable, energy efficient', 24.99),
('LIGHTING-003', 'Floor Lamp', 'Arc lamp, 3-way switch, adjustable height', 69.99),
('LIGHTING-004', 'Desk Lamp', 'LED, touch control, USB port', 29.99),
('LIGHTING-005', 'Night Light', 'LED, motion sensor, warm white', 14.99),
('STORAGE-001', 'External SSD', '1TB capacity, USB-C interface, portable', 89.99),
('STORAGE-002', 'External HDD', '2TB capacity, USB 3.0 interface, desktop external', 79.99),
('STORAGE-003', 'USB Flash Drive', '128GB capacity, USB 3.0 interface, metal casing', 19.99),
('STORAGE-004', 'Memory Card', '256GB microSD, UHS-I, adapter included', 34.99),
('STORAGE-005', 'Portable HDD', '1TB, USB 3.0, shock resistant', 89.99),
('NETWORK-001', 'WiFi Router', 'AC1900, gigabit ports, guest network', 79.99),
('NETWORK-002', 'Network Switch', '8-port gigabit, managed, desktop size', 129.99),
('NETWORK-003', 'Ethernet Cable', 'Cat6, 50ft length, molded connectors', 12.99),
('NETWORK-004', 'WiFi Extender', 'AC1200, dual-band, wall-plug design', 49.99),
('NETWORK-005', 'Network Cable', 'Cat6, 25ft, snagless, blue', 8.99);

-- Add customers
INSERT INTO customers (name, email, phone, address) VALUES
('Best Buy Store', 'store123@bestbuy.com', '555-1001', '456 Retail Ave, Minneapolis, MN'),
('Target Store', 'store456@target.com', '555-1002', '789 Retail Blvd, Chicago, IL'),
('Global Retail', 'wholesale@globalretail.com', '555-2001', '123 Wholesale St, Los Angeles, CA'),
('Walmart Supercenter', 'walmart789@walmart.com', '555-3001', '321 Retail Drive, Dallas, TX'),
('Home Depot', 'homedepot456@homedepot.com', '555-4001', '654 Hardware Blvd, Atlanta, GA'),
('Office Depot', 'officedepot123@officedepot.com', '555-5001', '987 Office Park, Phoenix, AZ'),
('Amazon Warehouse', 'amazon789@amazon.com', '555-6001', '456 Logistics Way, Seattle, WA'),
('Costco Wholesale', 'costco456@costco.com', '555-7001', '789 Bulk Buy Blvd, Denver, CO');

-- Add sample orders
INSERT INTO orders (order_number, customer_id, status, total_amount, notes) VALUES
('ORD-2024-001', 1, 'PROCESSING', 2599.98, 'Rush order for store opening'),
('ORD-2024-002', 2, 'SHIPPED', 149.97, 'Regular stock replenishment'),
('ORD-2024-003', 3, 'PENDING', 8999.95, 'Bulk wholesale order'),
('ORD-2024-004', 4, 'PROCESSING', 299.96, 'Store display setup'),
('ORD-2024-005', 5, 'COMPLETED', 449.95, 'Contractor supplies'),
('ORD-2024-006', 6, 'PROCESSING', 79.98, 'Office supplies order'),
('ORD-2024-007', 7, 'PENDING', 1799.97, 'Warehouse equipment'),
('ORD-2024-008', 8, 'SHIPPED', 2599.96, 'Bulk purchase order');

-- Add order items
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
((SELECT order_id FROM orders WHERE order_number = 'ORD-2024-001'), 1, 2, 1299.99),
((SELECT order_id FROM orders WHERE order_number = 'ORD-2024-002'), 21, 5, 19.99),
((SELECT order_id FROM orders WHERE order_number = 'ORD-2024-002'), 22, 5, 9.99),
((SELECT order_id FROM orders WHERE order_number = 'ORD-2024-003'), 1, 5, 1299.99),
((SELECT order_id FROM orders WHERE order_number = 'ORD-2024-003'), 2, 3, 799.99),
((SELECT order_id FROM orders WHERE order_number = 'ORD-2024-004'), 41, 2, 149.99),
((SELECT order_id FROM orders WHERE order_number = 'ORD-2024-005'), 42, 3, 149.99),
((SELECT order_id FROM orders WHERE order_number = 'ORD-2024-006'), 61, 4, 19.99),
((SELECT order_id FROM orders WHERE order_number = 'ORD-2024-007'), 51, 2, 89.99),
((SELECT order_id FROM orders WHERE order_number = 'ORD-2024-008'), 1, 2, 1299.99);

-- Add inventory records
INSERT INTO warehouse_inventory (warehouse_id, product_id, quantity) VALUES
(1, 1, 25), (1, 2, 30), (1, 3, 20), (1, 4, 15), (1, 5, 10),
(2, 6, 40), (2, 7, 35), (2, 8, 45), (2, 9, 30), (2, 10, 25),
(3, 11, 20), (3, 12, 15), (3, 13, 25), (3, 14, 30), (3, 15, 35),
(4, 16, 50), (4, 17, 45), (4, 18, 40), (4, 19, 55), (4, 20, 60),
(5, 21, 100), (5, 22, 95), (5, 23, 105), (5, 24, 110), (5, 25, 90);

-- Add sample documents for AI
INSERT INTO documents (title, content, document_type) VALUES
('WMS Overview', 'A Warehouse Management System (WMS) is software that helps manage warehouse operations including inventory tracking, order fulfillment, receiving, and shipping.', 'knowledge_base'),
('Inventory Management', 'Effective inventory management involves tracking stock levels, monitoring movements, and optimizing stock across multiple warehouse locations.', 'knowledge_base'),
('Order Processing', 'Order processing includes receiving orders, picking items, packing shipments, and managing order status throughout the fulfillment cycle.', 'knowledge_base'),
('Warehouse Operations', 'Warehouse operations include receiving goods, storing inventory, picking orders, and shipping products to customers efficiently.', 'knowledge_base'),
('Quality Control', 'Quality control in warehouse management ensures products meet standards through inspection, testing, and proper documentation.', 'knowledge_base');
" || echo "Sample data insertion completed"

echo ""
echo "=== Complete WMS Setup Finished ==="
echo ""
echo "Database Status:"
docker compose exec db psql -U wms_user -d warehouse_db -c "
SELECT 
    'users' as table_name, COUNT(*) as count FROM users
UNION ALL SELECT 'warehouses', COUNT(*) FROM warehouses
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'customers', COUNT(*) FROM customers
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'documents', COUNT(*) FROM documents
UNION ALL SELECT 'warehouse_inventory', COUNT(*) FROM warehouse_inventory
ORDER BY table_name;
"

echo ""
echo "Login Credentials:"
echo "Admin: admin@wms.com / Admin123!"
echo "Manager: manager@wms.com / Manager123!"
echo "Staff: staff@wms.com / Staff123!"
echo "User: user@wms.com / User123!"
echo ""
echo "Dashboard: http://localhost:8080"
echo "API: http://localhost:8000"
echo ""
echo "Next Steps:"
echo "1. Load AI knowledge base: uv run python3 wms_knowledge_base/load_wms_knowledge_base.py"
echo "2. Test AI functions: uv run python3 tests/test_ai_functions.py"
echo ""
echo "Setup complete! Your WMS system is ready for use."
