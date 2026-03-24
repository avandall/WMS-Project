import sqlite3

conn = sqlite3.connect('warehouse.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")
    
# Check if customer tables exist
for table_name in ['customers', 'customer_purchases']:
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    result = cursor.fetchone()
    if result:
        print(f"\n{table_name} schema:")
        print(result[0])

# Check documents table for customer_id column
cursor.execute("PRAGMA table_info(documents);")
columns = cursor.fetchall()
print("\nDocuments table columns:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

conn.close()
