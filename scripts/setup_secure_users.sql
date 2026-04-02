-- Secure Database Setup Script
-- Creates restricted database users with minimal permissions

-- Create read-only user for reporting
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'wms_readonly') THEN
        RAISE NOTICE 'Role wms_readonly already exists';
    ELSE
        CREATE ROLE wms_readonly WITH LOGIN PASSWORD 'readonly_password' NOINHERIT;
        RAISE NOTICE 'Role wms_readonly created';
    END IF;
END $$;

-- Create restricted user for write operations
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'wms_restricted') THEN
        RAISE NOTICE 'Role wms_restricted already exists';
    ELSE
        CREATE ROLE wms_restricted WITH LOGIN PASSWORD 'restricted_password' NOINHERIT;
        RAISE NOTICE 'Role wms_restricted created';
    END IF;
END $$;

-- Create admin user for maintenance
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'wms_admin') THEN
        RAISE NOTICE 'Role wms_admin already exists';
    ELSE
        CREATE ROLE wms_admin WITH LOGIN PASSWORD 'admin_password' NOINHERIT SUPERUSER;
        RAISE NOTICE 'Role wms_admin created';
    END IF;
END $$;

-- Grant read-only permissions to wms_readonly
GRANT CONNECT ON DATABASE warehouse_db TO wms_readonly;
GRANT USAGE ON SCHEMA public TO wms_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO wms_readonly;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO wms_readonly;

-- Grant limited write permissions to wms_restricted
GRANT CONNECT ON DATABASE warehouse_db TO wms_restricted;
GRANT USAGE ON SCHEMA public TO wms_restricted;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO wms_restricted;
GRANT INSERT ON products TO wms_restricted;
GRANT INSERT ON documents TO wms_restricted;
GRANT INSERT ON customers TO wms_restricted;
GRANT UPDATE ON products TO wms_restricted;
GRANT UPDATE ON customers TO wms_restricted;
GRANT UPDATE ON warehouse_inventory TO wms_restricted;
GRANT DELETE ON warehouse_inventory TO wms_restricted;
GRANT DELETE ON documents TO wms_restricted;
GRANT DELETE ON customers TO wms_restricted;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO wms_restricted;

-- Grant full permissions to wms_admin
GRANT CONNECT ON DATABASE warehouse_db TO wms_admin;
GRANT USAGE ON SCHEMA public TO wms_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO wms_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO wms_admin;

-- Create row-level security policies (PostgreSQL 15+)
-- This adds an extra layer of security by restricting access based on user role

-- Policy for read-only user - can only read
CREATE POLICY read_only_policy ON products
    FOR SELECT
    TO wms_readonly
    USING (true);

CREATE POLICY read_only_inventory_policy ON warehouse_inventory
    FOR SELECT
    TO wms_readonly
    USING (true);

-- Policy for restricted user - can read and write specific tables
CREATE POLICY restricted_products_policy ON products
    FOR ALL
    TO wms_restricted
    USING (true)
    WITH CHECK (true);

CREATE POLICY restricted_inventory_policy ON warehouse_inventory
    FOR ALL
    TO wms_restricted
    USING (true)
    WITH CHECK (true);

CREATE POLICY restricted_documents_policy ON documents
    FOR ALL
    TO wms_restricted
    USING (true)
    WITH CHECK (true);

CREATE POLICY restricted_customers_policy ON customers
    FOR ALL
    TO wms_restricted
    USING (true)
    WITH CHECK (true);

-- Enable row-level security
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE warehouse_inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

-- Create audit function to track database changes
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (table_name, operation, user_name, timestamp, record_id)
        VALUES (TG_TABLE_NAME, TG_OP, current_user, NOW(), OLD.id);
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (table_name, operation, user_name, timestamp, record_id)
        VALUES (TG_TABLE_NAME, TG_OP, current_user, NOW(), NEW.id);
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (table_name, operation, user_name, timestamp, record_id)
        VALUES (TG_TABLE_NAME, TG_OP, current_user, NEW.id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create audit logs table if it doesn't exist
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(10) NOT NULL,
    user_name VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    record_id INTEGER,
    old_values JSONB,
    new_values JSONB
);

-- Create audit trigger on products
DROP TRIGGER IF EXISTS products_audit_trigger;
CREATE TRIGGER products_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON products
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

-- Create audit trigger on warehouse_inventory
DROP TRIGGER IF EXISTS warehouse_inventory_audit_trigger;
CREATE TRIGGER warehouse_inventory_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON warehouse_inventory
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

-- Create audit trigger on documents
DROP TRIGGER IF EXISTS documents_audit_trigger;
CREATE TRIGGER documents_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

-- Create audit trigger on customers
DROP TRIGGER IF EXISTS customers_audit_trigger;
CREATE TRIGGER customers_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at);
CREATE INDEX IF NOT EXISTS idx_warehouse_inventory_product_id ON warehouse_inventory(product_id);
CREATE INDEX IF NOT EXISTS idx_warehouse_inventory_warehouse_id ON warehouse_inventory(warehouse_id);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_table_name ON audit_logs(table_name);

-- Create view for reporting (read-only user friendly)
CREATE OR REPLACE VIEW product_inventory_view AS
SELECT 
    p.id as product_id,
    p.name as product_name,
    p.price as unit_price,
    p.description,
    COALESCE(SUM(wi.quantity), 0) as total_quantity,
    COALESCE(SUM(wi.quantity * p.price), 0) as total_value
FROM products p
LEFT JOIN warehouse_inventory wi ON p.id = wi.product_id
GROUP BY p.id, p.name, p.price, p.description
WITH CHECK OPTION;

-- Grant access to the view
GRANT SELECT ON product_inventory_view TO wms_readonly;
GRANT SELECT ON product_inventory_view TO wms_restricted;

-- Create stored procedures for common operations
CREATE OR REPLACE FUNCTION get_product_inventory(p_product_id INTEGER)
RETURNS TABLE (
    warehouse_id INTEGER,
    quantity INTEGER,
    last_updated TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT warehouse_id, quantity, last_updated
    FROM warehouse_inventory
    WHERE product_id = p_product_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION safe_delete_product(p_product_id INTEGER, p_user_id VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    v_inventory_count INTEGER;
BEGIN
    -- Check if user has permission
    IF current_user != p_user_id THEN
        RAISE EXCEPTION 'Permission denied', 'ER0001';
    END IF;
    
    -- Check inventory constraints
    SELECT COUNT(*) INTO v_inventory_count
    FROM warehouse_inventory
    WHERE product_id = p_product_id AND quantity > 0;
    
    IF v_inventory_count > 0 THEN
        RAISE EXCEPTION 'Cannot delete product with active inventory', 'ER0002';
    END IF;
    
    -- Perform deletion
    DELETE FROM products WHERE id = p_product_id;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMIT;

-- Output setup completion
DO $$
BEGIN
    RAISE NOTICE 'Secure database setup completed successfully';
    RAISE NOTICE 'Users created: wms_readonly, wms_restricted, wms_admin';
    RAISE NOTICE 'Policies and triggers created for auditing';
    RAISE NOTICE 'Stored procedures created for secure operations';
END $$;
