"""
Unit tests for WarehouseService.
"""

import pytest
from unittest.mock import Mock, MagicMock
from PMKT.services.warehouse_service import WarehouseService
from PMKT.domain.warehouse_domain import Warehouse
from PMKT.domain.inventory_domain import InventoryItem
from PMKT.module.custom_exceptions import (
    ValidationError, WarehouseNotFoundError, InsufficientStockError, ProductNotFoundError
)


class TestWarehouseService:
    """Test cases for WarehouseService."""

    @pytest.fixture
    def mock_repo(self):
        """Mock warehouse repository."""
        return Mock()

    @pytest.fixture
    def mock_id_generator(self):
        """Mock ID generator."""
        return Mock(return_value=123)

    @pytest.fixture
    def warehouse_service(self, mock_repo, monkeypatch, mock_id_generator):
        """Warehouse service with mocked dependencies."""
        service = WarehouseService(mock_repo)
        # Mock the ID generator
        monkeypatch.setattr(service, '_warehouse_id_generator', mock_id_generator)
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

    def test_add_product_to_warehouse_success(self, warehouse_service, mock_repo):
        """Test adding product to warehouse successfully."""
        # Act
        warehouse_service.add_product_to_warehouse(1, 100, 10)

        # Assert
        mock_repo.add_product_to_warehouse.assert_called_once_with(1, 100, 10)

    def test_add_product_to_warehouse_validation_error(self, warehouse_service, mock_repo):
        """Test adding product to warehouse with validation error."""
        # Arrange
        mock_repo.add_product_to_warehouse.side_effect = ValidationError("Invalid quantity")

        # Act & Assert
        with pytest.raises(ValidationError, match="Invalid quantity"):
            warehouse_service.add_product_to_warehouse(1, 100, -5)

        mock_repo.add_product_to_warehouse.assert_called_once_with(1, 100, -5)

    def test_add_product_to_warehouse_not_found(self, warehouse_service, mock_repo):
        """Test adding product to non-existent warehouse."""
        # Arrange
        mock_repo.add_product_to_warehouse.side_effect = WarehouseNotFoundError("Warehouse not found")

        # Act & Assert
        with pytest.raises(WarehouseNotFoundError, match="Warehouse not found"):
            warehouse_service.add_product_to_warehouse(999, 100, 10)

        mock_repo.add_product_to_warehouse.assert_called_once_with(999, 100, 10)

    def test_remove_product_from_warehouse_success(self, warehouse_service, mock_repo):
        """Test removing product from warehouse successfully."""
        # Act
        warehouse_service.remove_product_from_warehouse(1, 100, 5)

        # Assert
        mock_repo.remove_product_from_warehouse.assert_called_once_with(1, 100, 5)

    def test_remove_product_from_warehouse_insufficient_stock(self, warehouse_service, mock_repo):
        """Test removing product with insufficient stock."""
        # Arrange
        mock_repo.remove_product_from_warehouse.side_effect = InsufficientStockError("Insufficient stock")

        # Act & Assert
        with pytest.raises(InsufficientStockError, match="Insufficient stock"):
            warehouse_service.remove_product_from_warehouse(1, 100, 50)

        mock_repo.remove_product_from_warehouse.assert_called_once_with(1, 100, 50)

    def test_remove_product_from_warehouse_not_found(self, warehouse_service, mock_repo):
        """Test removing product from non-existent warehouse."""
        # Arrange
        mock_repo.remove_product_from_warehouse.side_effect = WarehouseNotFoundError("Warehouse not found")

        # Act & Assert
        with pytest.raises(WarehouseNotFoundError, match="Warehouse not found"):
            warehouse_service.remove_product_from_warehouse(999, 100, 5)

        mock_repo.remove_product_from_warehouse.assert_called_once_with(999, 100, 5)

    def test_get_warehouse_inventory_success(self, warehouse_service, mock_repo):
        """Test getting warehouse inventory successfully."""
        # Arrange
        mock_inventory = [
            {"product_id": 1, "quantity": 10},
            {"product_id": 2, "quantity": 5}
        ]
        mock_repo.get_warehouse_inventory.return_value = mock_inventory

        # Act
        result = warehouse_service.get_warehouse_inventory(1)

        # Assert
        assert result == mock_inventory
        mock_repo.get_warehouse_inventory.assert_called_once_with(1)

    def test_get_warehouse_inventory_not_found(self, warehouse_service, mock_repo):
        """Test getting inventory for non-existent warehouse."""
        # Arrange
        mock_repo.get_warehouse_inventory.side_effect = WarehouseNotFoundError("Warehouse not found")

        # Act & Assert
        with pytest.raises(WarehouseNotFoundError, match="Warehouse not found"):
            warehouse_service.get_warehouse_inventory(999)

        mock_repo.get_warehouse_inventory.assert_called_once_with(999)

    def test_create_warehouse_success(self, warehouse_service, mock_repo, mock_id_generator):
        """Test creating a warehouse successfully."""
        # Arrange
        expected_warehouse = Warehouse(warehouse_id=123, location="New Warehouse")
        mock_repo.create_warehouse.return_value = None

        # Act
        result = warehouse_service.create_warehouse("New Warehouse")

        # Assert
        assert result.warehouse_id == 123
        assert result.location == "New Warehouse"
        assert result.inventory == []
        mock_id_generator.assert_called_once()
        mock_repo.create_warehouse.assert_called_once()
        # Verify the warehouse passed to repo has correct data
        call_args = mock_repo.create_warehouse.call_args[0][0]
        assert call_args.warehouse_id == 123
        assert call_args.location == "New Warehouse"

    def test_create_warehouse_validation_error(self, warehouse_service, mock_repo, mock_id_generator):
        """Test creating a warehouse with validation error."""
        # Act & Assert
        with pytest.raises(ValidationError, match="Warehouse location cannot be empty"):
            warehouse_service.create_warehouse("")

        # The validation happens in the domain layer before calling the repo
        mock_id_generator.assert_called_once()
        mock_repo.create_warehouse.assert_not_called()

    def test_create_warehouse_with_id_success(self, warehouse_service, mock_repo, sample_warehouse):
        """Test creating a warehouse with pre-defined ID successfully."""
        # Act
        warehouse_service.create_warehouse_with_id(sample_warehouse)

        # Assert
        mock_repo.create_warehouse.assert_called_once_with(sample_warehouse)

    def test_create_warehouse_with_id_already_exists(self, warehouse_service, mock_repo, sample_warehouse):
        """Test creating a warehouse that already exists."""
        # Arrange
        from PMKT.module.custom_exceptions import EntityAlreadyExistsError
        mock_repo.create_warehouse.side_effect = EntityAlreadyExistsError("Warehouse already exists")

        # Act & Assert
        with pytest.raises(EntityAlreadyExistsError, match="Warehouse already exists"):
            warehouse_service.create_warehouse_with_id(sample_warehouse)

        mock_repo.create_warehouse.assert_called_once_with(sample_warehouse)