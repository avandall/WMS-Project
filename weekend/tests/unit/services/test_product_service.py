"""
Unit tests for ProductService.
"""

import pytest
from unittest.mock import Mock, MagicMock
from app.services.product_service import ProductService
from app.models.product_domain import Product
from app.exceptions.business_exceptions import ValidationError, EntityNotFoundError


class TestProductService:
    """Test cases for ProductService."""

    @pytest.fixture
    def mock_repo(self):
        """Mock product repository."""
        return Mock()

    @pytest.fixture
    def product_service(self, mock_repo):
        """Product service with mocked repository."""
        return ProductService(mock_repo)

    @pytest.fixture
    def sample_product(self):
        """Sample product for testing."""
        return Product(
            product_id=1,
            name="Test Product",
            description="A test product",
            price=29.99
        )

    def test_create_product_success(self, product_service, mock_repo, sample_product):
        """Test creating a product successfully."""
        # Arrange
        mock_repo.create_product.return_value = sample_product

        # Act
        result = product_service.create_product(1, "Test Product", 29.99, "A test product")

        # Assert
        assert result == sample_product
        mock_repo.create_product.assert_called_once_with(1, "Test Product", 29.99, "A test product")

    def test_create_product_minimal(self, product_service, mock_repo, sample_product):
        """Test creating a product with minimal data."""
        # Arrange
        mock_repo.create_product.return_value = sample_product

        # Act
        result = product_service.create_product(1, "Test Product", 29.99)

        # Assert
        assert result == sample_product
        mock_repo.create_product.assert_called_once_with(1, "Test Product", 29.99, None)

    def test_create_product_validation_error(self, product_service, mock_repo):
        """Test creating a product with validation error."""
        # Arrange
        mock_repo.create_product.side_effect = ValidationError("Invalid product data")

        # Act & Assert
        with pytest.raises(ValidationError, match="Invalid product data"):
            product_service.create_product(1, "", 29.99)

        mock_repo.create_product.assert_called_once_with(1, "", 29.99, None)

    def test_get_product_details_success(self, product_service, mock_repo, sample_product):
        """Test getting product details successfully."""
        # Arrange
        mock_repo.get_product_details.return_value = sample_product

        # Act
        result = product_service.get_product_details(1)

        # Assert
        assert result == sample_product
        mock_repo.get_product_details.assert_called_once_with(1)

    def test_get_product_details_not_found(self, product_service, mock_repo):
        """Test getting product details for non-existent product."""
        # Arrange
        mock_repo.get_product_details.side_effect = EntityNotFoundError("Product not found")

        # Act & Assert
        with pytest.raises(EntityNotFoundError, match="Product not found"):
            product_service.get_product_details(999)

        mock_repo.get_product_details.assert_called_once_with(999)

    def test_update_product_success(self, product_service, mock_repo, sample_product):
        """Test updating a product successfully."""
        # Arrange
        updated_product = Product(
            product_id=1,
            name="Updated Product",
            description="Updated description",
            price=39.99
        )
        mock_repo.update_product.return_value = updated_product

        # Act
        result = product_service.update(1, name="Updated Product", price=39.99, description="Updated description")

        # Assert
        assert result == updated_product
        mock_repo.update_product.assert_called_once_with(1, "Updated Product", 39.99, "Updated description")

    def test_update_product_partial(self, product_service, mock_repo, sample_product):
        """Test updating a product with partial data."""
        # Arrange
        mock_repo.update_product.return_value = sample_product

        # Act
        result = product_service.update(1, price=39.99)

        # Assert
        assert result == sample_product
        mock_repo.update_product.assert_called_once_with(1, None, 39.99, None)

    def test_update_product_not_found(self, product_service, mock_repo):
        """Test updating a non-existent product."""
        # Arrange
        mock_repo.update_product.side_effect = EntityNotFoundError("Product not found")

        # Act & Assert
        with pytest.raises(EntityNotFoundError, match="Product not found"):
            product_service.update(999, price=39.99)

        mock_repo.update_product.assert_called_once_with(999, None, 39.99, None)

    def test_delete_product_success(self, product_service, mock_repo):
        """Test deleting a product successfully."""
        # Act
        product_service.delete_product(1)

        # Assert
        mock_repo.delete.assert_called_once_with(1)

    def test_delete_product_not_found(self, product_service, mock_repo):
        """Test deleting a non-existent product."""
        # Arrange
        mock_repo.delete.side_effect = EntityNotFoundError("Product not found")

        # Act & Assert
        with pytest.raises(EntityNotFoundError, match="Product not found"):
            product_service.delete_product(999)

        mock_repo.delete.assert_called_once_with(999)