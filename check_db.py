import sqlite3
import os

os.chdir('d:\\Hoc\\First_Project\\WMS')
conn = sqlite3.connect('warehouse.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables in database:', [t[0] for t in tables])
for table in [t[0] for t in tables]:
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    count = cursor.fetchone()[0]
    print(f'  {table}: {count} rows')
conn.close()
