"""
Unit tests for WarehouseService.
"""

import pytest
from unittest.mock import Mock, MagicMock
from app.services.warehouse_service import WarehouseService
from app.models.warehouse_domain import Warehouse
from app.models.inventory_domain import InventoryItem
from app.exceptions.business_exceptions import (
    ValidationError, WarehouseNotFoundError, InsufficientStockError, ProductNotFoundError, InvalidQuantityError
)


class TestWarehouseService:
    """Test cases for WarehouseService."""

    @pytest.fixture
    def mock_warehouse_repo(self):
        """Mock warehouse repository."""
        return Mock()

    @pytest.fixture
    def mock_product_repo(self):
        """Mock product repository."""
        return Mock()

    @pytest.fixture
    def mock_inventory_repo(self):
        """Mock inventory repository."""
        return Mock()

    @pytest.fixture
    def mock_id_generator(self):
        """Mock ID generator."""
        return Mock(return_value=123)

    @pytest.fixture
    def warehouse_service(self, mock_warehouse_repo, mock_product_repo, mock_inventory_repo, monkeypatch, mock_id_generator):
        """Warehouse service with mocked dependencies."""
        service = WarehouseService(mock_warehouse_repo, mock_product_repo, mock_inventory_repo)
        # Mock the ID generator
        monkeypatch.setattr(service, '_warehouse_id_generator', mock_id_generator)
        # Mock inventory repo to return sufficient quantity
        mock_inventory_repo.get_quantity.return_value = 100
        return service

    @pytest.fixture
    def sample_warehouse(self):
        """Sample warehouse for testing."""
        return Warehouse(
            warehouse_id=1,
            location="Test Warehouse",
            inventory=[
                InventoryItem(product_id=1, quantity=10),
                InventoryItem(product_id=2, quantity=5)
            ]
        )

    def test_add_product_to_warehouse_success(self, warehouse_service, mock_warehouse_repo, mock_product_repo, mock_inventory_repo):
        """Test adding product to warehouse successfully."""
        # Arrange
        from app.models.warehouse_domain import Warehouse
        mock_warehouse = Warehouse(warehouse_id=1, location="Test Warehouse")
        mock_product = Mock()
        mock_product.product_id = 100
        
        mock_warehouse_repo.get.return_value = mock_warehouse
        mock_product_repo.get.return_value = mock_product
        mock_inventory_repo.get_quantity.return_value = 50  # Total available
        mock_warehouse_repo.get_warehouse_inventory.return_value = []  # No existing inventory
        
        # Act
        warehouse_service.add_product_to_warehouse(1, 100, 10)

        # Assert
        mock_warehouse_repo.add_product_to_warehouse.assert_called_once_with(1, 100, 10)

    def test_add_product_to_warehouse_validation_error(self, warehouse_service, mock_warehouse_repo):
        """Test adding product to warehouse with validation error."""
        # Act & Assert
        with pytest.raises(InvalidQuantityError, match="Quantity must be positive"):
            warehouse_service.add_product_to_warehouse(1, 100, -5)

    def test_add_product_to_warehouse_not_found(self, warehouse_service, mock_warehouse_repo):
        """Test adding product to non-existent warehouse."""
        # Arrange
        mock_warehouse_repo.add_product_to_warehouse.side_effect = WarehouseNotFoundError("Warehouse not found")
        mock_warehouse_repo.get_warehouse_inventory.return_value = []

        # Act & Assert
        with pytest.raises(WarehouseNotFoundError, match="Warehouse not found"):
            warehouse_service.add_product_to_warehouse(999, 100, 10)

        mock_warehouse_repo.add_product_to_warehouse.assert_called_once_with(999, 100, 10)

    def test_remove_product_from_warehouse_success(self, warehouse_service, mock_warehouse_repo):
        """Test removing product from warehouse successfully."""
        # Arrange
        from app.models.inventory_domain import InventoryItem
        mock_warehouse_repo.get_warehouse_inventory.return_value = [InventoryItem(product_id=100, quantity=10)]
        
        # Act
        warehouse_service.remove_product_from_warehouse(1, 100, 5)

        # Assert
        mock_warehouse_repo.remove_product_from_warehouse.assert_called_once_with(1, 100, 5)

    def test_remove_product_from_warehouse_insufficient_stock(self, warehouse_service, mock_warehouse_repo):
        """Test removing product with insufficient stock."""
        # Arrange
        from app.models.inventory_domain import InventoryItem
        mock_warehouse_repo.get_warehouse_inventory.return_value = [InventoryItem(product_id=100, quantity=10)]

        # Act & Assert
        with pytest.raises(InsufficientStockError, match="Insufficient stock in warehouse"):
            warehouse_service.remove_product_from_warehouse(1, 100, 50)

    def test_remove_product_from_warehouse_not_found(self, warehouse_service, mock_warehouse_repo):
        """Test removing product from non-existent warehouse."""
        # Arrange
        from app.models.inventory_domain import InventoryItem
        mock_warehouse_repo.remove_product_from_warehouse.side_effect = WarehouseNotFoundError("Warehouse not found")
        mock_warehouse_repo.get_warehouse_inventory.return_value = [InventoryItem(product_id=100, quantity=10)]

        # Act & Assert
        with pytest.raises(WarehouseNotFoundError, match="Warehouse not found"):
            warehouse_service.remove_product_from_warehouse(999, 100, 5)

        mock_warehouse_repo.remove_product_from_warehouse.assert_called_once_with(999, 100, 5)

    def test_get_warehouse_inventory_success(self, warehouse_service, mock_warehouse_repo, mock_product_repo):
        """Test getting warehouse inventory successfully."""
        # Arrange
        from app.models.inventory_domain import InventoryItem
        mock_inventory = [
            InventoryItem(product_id=1, quantity=10),
            InventoryItem(product_id=2, quantity=5)
        ]
        mock_warehouse_repo.get_warehouse_inventory.return_value = mock_inventory
        
        # Mock product repo
        mock_product1 = Mock()
        mock_product1.product_id = 1
        mock_product1.name = "Product 1"
        mock_product1.price = 10.0
        
        mock_product2 = Mock()
        mock_product2.product_id = 2
        mock_product2.name = "Product 2"
        mock_product2.price = 20.0
        
        mock_product_repo.get.side_effect = lambda pid: mock_product1 if pid == 1 else mock_product2

        # Act
        result = warehouse_service.get_warehouse_inventory(1)

        # Assert
        assert len(result) == 2
        assert result[0]["product"] == mock_product1
        assert result[0]["quantity"] == 10
        assert result[1]["product"] == mock_product2
        assert result[1]["quantity"] == 5
        mock_warehouse_repo.get_warehouse_inventory.assert_called_once_with(1)

    def test_get_warehouse_inventory_not_found(self, warehouse_service, mock_warehouse_repo):
        """Test getting inventory for non-existent warehouse."""
        # Arrange
        mock_warehouse_repo.get_warehouse_inventory.side_effect = WarehouseNotFoundError("Warehouse not found")

        # Act & Assert
        with pytest.raises(WarehouseNotFoundError, match="Warehouse not found"):
            warehouse_service.get_warehouse_inventory(999)

        mock_warehouse_repo.get_warehouse_inventory.assert_called_once_with(999)

    def test_create_warehouse_success(self, warehouse_service, mock_warehouse_repo, mock_id_generator):
        """Test creating a warehouse successfully."""
        # Arrange
        expected_warehouse = Warehouse(warehouse_id=123, location="New Warehouse")
        mock_warehouse_repo.create_warehouse.return_value = None

        # Act
        result = warehouse_service.create_warehouse("New Warehouse")

        # Assert
        assert result.warehouse_id == 123
        assert result.location == "New Warehouse"
        assert result.inventory == []
        mock_id_generator.assert_called_once()
        mock_warehouse_repo.create_warehouse.assert_called_once()
        # Verify the warehouse passed to repo has correct data
        call_args = mock_warehouse_repo.create_warehouse.call_args[0][0]
        assert call_args.warehouse_id == 123
        assert call_args.location == "New Warehouse"

    def test_create_warehouse_validation_error(self, warehouse_service, mock_warehouse_repo, mock_id_generator):
        """Test creating a warehouse with validation error."""
        # Act & Assert
        with pytest.raises(ValidationError, match="Warehouse location cannot be empty"):
            warehouse_service.create_warehouse("")

        # The validation happens in the domain layer before calling the repo
        mock_id_generator.assert_called_once()
        mock_warehouse_repo.create_warehouse.assert_not_called()

    def test_create_warehouse_with_id_success(self, warehouse_service, mock_warehouse_repo, sample_warehouse):
        """Test creating a warehouse with pre-defined ID successfully."""        # Arrange
        mock_warehouse_repo.get.return_value = None
                # Act
        warehouse_service.create_warehouse_with_id(sample_warehouse)

        # Assert
        mock_warehouse_repo.create_warehouse.assert_called_once_with(sample_warehouse)

    def test_create_warehouse_with_id_already_exists(self, warehouse_service, mock_warehouse_repo, sample_warehouse):
        """Test creating a warehouse that already exists."""
        # Arrange
        from app.exceptions.business_exceptions import EntityAlreadyExistsError
        mock_warehouse_repo.get.return_value = sample_warehouse

        # Act & Assert
        with pytest.raises(EntityAlreadyExistsError, match="Warehouse with ID 1 already exists"):
            warehouse_service.create_warehouse_with_id(sample_warehouse)