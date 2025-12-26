"""
Unit tests for ProductRepo.
"""

import pytest
from unittest.mock import Mock
from app.repositories.sql.product_repo import ProductRepo
from app.models.product_domain import Product
from app.exceptions.business_exceptions import ValidationError


class TestProductRepo:
    """Test cases for ProductRepo."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repo = ProductRepo()

    def test_save_and_get_product(self):
        """Test saving and retrieving a product."""
        product = Product(product_id=1, name="Test Product", price=10.0)

        self.repo.save(product)
        retrieved = self.repo.get(1)

        assert retrieved is not None
        assert retrieved.product_id == 1
        assert retrieved.name == "Test Product"
        assert retrieved.price == 10.0

    def test_get_nonexistent_product(self):
        """Test getting a product that doesn't exist."""
        result = self.repo.get(999)
        assert result is None

    def test_get_price_existing_product(self):
        """Test getting price of existing product."""
        product = Product(product_id=1, name="Test Product", price=15.5)
        self.repo.save(product)

        price = self.repo.get_price(1)
        assert price == 15.5

    def test_get_price_nonexistent_product(self):
        """Test getting price of nonexistent product raises KeyError."""
        with pytest.raises(KeyError, match="Product not found"):
            self.repo.get_price(999)

    def test_delete_existing_product(self):
        """Test deleting an existing product."""
        product = Product(product_id=1, name="Test Product", price=10.0)
        self.repo.save(product)

        self.repo.delete(1)
        assert self.repo.get(1) is None

    def test_delete_nonexistent_product(self):
        """Test deleting a nonexistent product raises KeyError."""
        with pytest.raises(KeyError, match="Product not found"):
            self.repo.delete(999)

    def test_create_product(self):
        """Test creating a new product."""
        product = self.repo.create_product(
            product_id=1,
            name="New Product",
            price=25.0,
            description="A test product"
        )

        assert product.product_id == 1
        assert product.name == "New Product"
        assert product.price == 25.0
        assert product.description == "A test product"

        # Verify it's saved
        retrieved = self.repo.get(1)
        assert retrieved is not None
        assert retrieved.name == "New Product"

    def test_create_product_without_description(self):
        """Test creating a product without description."""
        product = self.repo.create_product(
            product_id=2,
            name="Product No Desc",
            price=30.0
        )

        assert product.description is None

    def test_get_product_details_existing(self):
        """Test getting product details for existing product."""
        product = Product(product_id=1, name="Test", price=10.0, description="Desc")
        self.repo.save(product)

        details = self.repo.get_product_details(1)
        assert details.product_id == 1
        assert details.name == "Test"
        assert details.price == 10.0
        assert details.description == "Desc"

    def test_get_product_details_nonexistent(self):
        """Test getting product details for nonexistent product raises KeyError."""
        with pytest.raises(KeyError, match="Product not found"):
            self.repo.get_product_details(999)

    def test_update_product_all_fields(self):
        """Test updating all fields of a product."""
        product = Product(product_id=1, name="Original", price=10.0, description="Original desc")
        self.repo.save(product)

        updated = self.repo.update_product(
            product_id=1,
            name="Updated Name",
            price=20.0,
            description="Updated desc"
        )

        assert updated.name == "Updated Name"
        assert updated.price == 20.0
        assert updated.description == "Updated desc"

        # Verify persistence
        retrieved = self.repo.get(1)
        assert retrieved.name == "Updated Name"
        assert retrieved.price == 20.0
        assert retrieved.description == "Updated desc"

    def test_update_product_partial_fields(self):
        """Test updating only some fields of a product."""
        product = Product(product_id=1, name="Original", price=10.0, description="Original desc")
        self.repo.save(product)

        updated = self.repo.update_product(product_id=1, price=15.0)

        assert updated.name == "Original"  # Unchanged
        assert updated.price == 15.0  # Changed
        assert updated.description == "Original desc"  # Unchanged

    def test_update_product_nonexistent(self):
        """Test updating a nonexistent product raises KeyError."""
        with pytest.raises(KeyError, match="Product not found"):
            self.repo.update_product(product_id=999, name="New Name")

    def test_update_product_invalid_name(self):
        """Test updating product with invalid name raises ValidationError."""
        product = Product(product_id=1, name="Valid", price=10.0)
        self.repo.save(product)

        with pytest.raises(ValidationError):
            self.repo.update_product(product_id=1, name="")  # Empty name

    def test_update_product_invalid_price(self):
        """Test updating product with invalid price raises ValidationError."""
        product = Product(product_id=1, name="Valid", price=10.0)
        self.repo.save(product)

        with pytest.raises(ValidationError):
            self.repo.update_product(product_id=1, price=-5.0)  # Negative price

    def test_multiple_products(self):
        """Test handling multiple products."""
        product1 = Product(product_id=1, name="Product 1", price=10.0)
        product2 = Product(product_id=2, name="Product 2", price=20.0)
        product3 = Product(product_id=3, name="Product 3", price=30.0)

        self.repo.save(product1)
        self.repo.save(product2)
        self.repo.save(product3)

        assert self.repo.get(1).name == "Product 1"
        assert self.repo.get(2).name == "Product 2"
        assert self.repo.get(3).name == "Product 3"

        # Delete middle product
        self.repo.delete(2)
        assert self.repo.get(2) is None
        assert self.repo.get(1) is not None
        assert self.repo.get(3) is not None