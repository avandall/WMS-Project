import sqlite3

conn = sqlite3.connect('warehouse.db')
cursor = conn.cursor()

# Check if customer_id column exists
cursor.execute("PRAGMA table_info(documents);")
columns = cursor.fetchall()
column_names = [col[1] for col in columns]

if 'customer_id' not in column_names:
    print("Adding customer_id column to documents table...")
    cursor.execute("ALTER TABLE documents ADD COLUMN customer_id INTEGER;")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_customer_id ON documents(customer_id);")
    conn.commit()
    print("✓ customer_id column added")
else:
    print("✓ customer_id column already exists")

# Verify
cursor.execute("PRAGMA table_info(documents);")
columns = cursor.fetchall()
print("\nDocuments table columns:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

conn.close()
