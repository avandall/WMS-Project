"""
Create default admin user if not exists
"""
import sqlite3
import bcrypt

conn = sqlite3.connect('warehouse.db')
cursor = conn.cursor()

# Check if admin user exists
cursor.execute("SELECT email FROM users WHERE email='admin@example.com';")
result = cursor.fetchone()

if not result:
    # Create admin user with password "admin" using bcrypt
    password_bytes = "admin".encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    password_hash = hashed.decode('utf-8')
    
    cursor.execute("""
        INSERT INTO users (email, hashed_password, role, full_name, is_active)
        VALUES (?, ?, ?, ?, ?)
    """, ('admin@example.com', password_hash, 'admin', 'Admin User', 1))
    
    conn.commit()
    print("✓ Admin user created: admin@example.com / admin")
else:
    # Update existing admin password
    password_bytes = "admin".encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    password_hash = hashed.decode('utf-8')
    
    cursor.execute("""
        UPDATE users 
        SET hashed_password = ?, role = 'admin'
        WHERE email = 'admin@example.com'
    """, (password_hash,))
    
    conn.commit()
    print("✓ Admin user password updated: admin@example.com / admin")

conn.close()
