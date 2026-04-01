import sqlite3

conn = sqlite3.connect('warehouse.db')
cursor = conn.cursor()

# Get warehouse table schema
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='warehouses';")
result = cursor.fetchone()
if result:
    print("Warehouses table schema:")
    print(result[0])

# Check existing warehouses
cursor.execute("SELECT warehouse_id, location FROM warehouses ORDER BY warehouse_id;")
warehouses = cursor.fetchall()
print(f"\nExisting warehouses: {len(warehouses)}")
for wh in warehouses:
    print(f"  W-{wh[0]}: {wh[1]}")

conn.close()
