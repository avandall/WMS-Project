"""Secure product repository with SQL hardening measures."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.core.secure_database import get_readonly_session, get_restricted_session
from app.core.secure_query import SecureQueryBuilder, SecureRepository, SecureQueries
from app.core.logging import get_logger
from app.domain.entities.product import Product
from app.domain.interfaces.product_repo import ProductRepo

logger = get_logger(__name__)

class SecureProductRepository(ProductRepo, SecureRepository):
    """Secure implementation of product repository."""
    
    def __init__(self, session: Session = None):
        if session is None:
            session = get_restricted_session()  # Use restricted session for writes
        super().__init__(session)
        self.readonly_session = get_readonly_session()  # Separate session for reads
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Product]:
        """Get all products with pagination using secure queries."""
        try:
            query, params = SecureQueryBuilder("products") \
                .select() \
                .limit(limit) \
                .offset(offset) \
                .build()
            
            rows = self.execute_secure_query(query, params)
            
            products = []
            for row in rows:
                try:
                    product = Product(
                        product_id=row['id'],
                        name=row['name'],
                        price=float(row['price']),
                        description=row.get('description', '')
                    )
                    products.append(product)
                except (KeyError, ValueError, TypeError) as e:
                    logger.warning(f"Invalid product data in row: {row}, error: {e}")
                    continue
            
            logger.info(f"Retrieved {len(products)} products")
            return products
            
        except Exception as e:
            logger.error(f"Failed to get all products: {str(e)}")
            raise
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID using secure parameterized query."""
        try:
            query = SecureQueries.get_by_id("products", "product_id")
            params = {"id": product_id}
            
            row = self.execute_secure_scalar(query, params)
            
            if not row:
                return None
            
            product = Product(
                product_id=row['id'],
                name=row['name'],
                price=float(row['price']),
                description=row.get('description', '')
            )
            
            logger.info(f"Retrieved product {product_id}: {product.name}")
            return product
            
        except Exception as e:
            logger.error(f"Failed to get product {product_id}: {str(e)}")
            raise
    
    def create(self, product: Product) -> Product:
        """Create product using secure parameterized query."""
        try:
            query = """
                INSERT INTO products (name, price, description, created_at) 
                VALUES (:name, :price, :description, NOW())
                RETURNING id, name, price, description, created_at
            """
            
            params = {
                "name": product.name,
                "price": product.price,
                "description": product.description or ""
            }
            
            result = self.execute_secure_scalar(query, params)
            
            created_product = Product(
                product_id=result['id'],
                name=result['name'],
                price=float(result['price']),
                description=result.get('description', '')
            )
            
            logger.info(f"Created product: {created_product.name} (ID: {created_product.product_id})")
            return created_product
            
        except Exception as e:
            logger.error(f"Failed to create product: {str(e)}")
            self.session.rollback()
            raise
    
    def update(self, product_id: int, product: Product) -> Product:
        """Update product using secure parameterized query."""
        try:
            query = """
                UPDATE products 
                SET name = :name, price = :price, description = :description, updated_at = NOW()
                WHERE product_id = :product_id
                RETURNING id, name, price, description, updated_at
            """
            
            params = {
                "product_id": product_id,
                "name": product.name,
                "price": product.price,
                "description": product.description or ""
            }
            
            result = self.execute_secure_scalar(query, params)
            
            updated_product = Product(
                product_id=result['id'],
                name=result['name'],
                price=float(result['price']),
                description=result.get('description', '')
            )
            
            logger.info(f"Updated product {product_id}: {updated_product.name}")
            return updated_product
            
        except Exception as e:
            logger.error(f"Failed to update product {product_id}: {str(e)}")
            self.session.rollback()
            raise
    
    def delete(self, product_id: int) -> None:
        """Delete product using secure parameterized query with foreign key checks."""
        try:
            # First check if product exists and get details for logging
            check_query = SecureQueries.get_by_id("products", "product_id")
            existing = self.execute_secure_scalar(check_query, {"id": product_id})
            
            if not existing:
                raise ValueError(f"Product {product_id} not found")
            
            # Check for foreign key constraints
            constraint_check_query = """
                SELECT 
                    COUNT(*) as inventory_count,
                    COUNT(*) FILTER (WHERE quantity > 0) as active_inventory
                FROM warehouse_inventory 
                WHERE product_id = :product_id
            """
            
            constraint_result = self.execute_secure_scalar(constraint_check_query, {"product_id": product_id})
            
            if constraint_result['active_inventory'] > 0:
                raise ValueError(f"Cannot delete product {product_id}: has active inventory items")
            
            # Perform the deletion
            delete_query = SecureQueries.safe_delete("products", "product_id")
            params = {"product_id": product_id}
            
            self.session.execute(text(delete_query), params)
            self.session.commit()
            
            logger.info(f"Deleted product {product_id}: {existing['name']}")
            
        except ValueError as e:
            logger.warning(f"Delete validation failed for product {product_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to delete product {product_id}: {str(e)}")
            self.session.rollback()
            raise
    
    def search(self, search_term: str, limit: int = 50) -> List[Product]:
        """Search products using secure parameterized query."""
        try:
            query = """
                SELECT id, name, price, description 
                FROM products 
                WHERE name ILIKE :search_term OR description ILIKE :search_term
                ORDER BY name 
                LIMIT :limit
            """
            
            params = {
                "search_term": f"%{search_term}%",
                "limit": limit
            }
            
            rows = self.execute_secure_query(query, params)
            
            products = []
            for row in rows:
                try:
                    product = Product(
                        product_id=row['id'],
                        name=row['name'],
                        price=float(row['price']),
                        description=row.get('description', '')
                    )
                    products.append(product)
                except (KeyError, ValueError, TypeError) as e:
                    logger.warning(f"Invalid product data in search result: {row}, error: {e}")
                    continue
            
            logger.info(f"Search for '{search_term}' returned {len(products)} products")
            return products
            
        except Exception as e:
            logger.error(f"Failed to search products: {str(e)}")
            raise
    
    def get_inventory_count(self, product_id: int) -> int:
        """Get inventory count for a product using read-only session."""
        try:
            query = """
                SELECT COALESCE(SUM(quantity), 0) as total_quantity
                FROM warehouse_inventory 
                WHERE product_id = :product_id
            """
            
            params = {"product_id": product_id}
            
            # Use read-only session for this query
            with self.readonly_session() as readonly_db:
                result = readonly_db.execute(text(query), params)
                count = result.scalar()
            
            logger.info(f"Product {product_id} has inventory count: {count}")
            return count
            
        except Exception as e:
            logger.error(f"Failed to get inventory count for product {product_id}: {str(e)}")
            return 0
    
    def exists(self, product_id: int) -> bool:
        """Check if product exists using secure query."""
        try:
            query = SecureQueries.check_exists("products", "product_id = :product_id")
            params = {"product_id": product_id}
            
            result = self.execute_secure_scalar(query, params)
            return result is not None
            
        except Exception as e:
            logger.error(f"Failed to check product existence {product_id}: {str(e)}")
            return False
