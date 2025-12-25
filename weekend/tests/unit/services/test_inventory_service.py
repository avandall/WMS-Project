"""
Unit tests for InventoryService.
"""

import pytest
from unittest.mock import Mock
from PMKT.services.inventory_service import InventoryService
from PMKT.module.custom_exceptions import ValidationError, EntityNotFoundError


class TestInventoryService:
    """Test cases for InventoryService."""

    @pytest.fixture
    def mock_repo(self):
        """Mock inventory repository."""
        return Mock()

    @pytest.fixture
    def inventory_service(self, mock_repo):
        """Inventory service with mocked repository."""
        return InventoryService(mock_repo)

    def test_add_to_total_success(self, inventory_service, mock_repo):
        """Test adding quantity to total inventory successfully."""
        # Act
        inventory_service.add_to_total(1, 10)

        # Assert
        mock_repo.add_quantity.assert_called_once_with(1, 10)

    def test_add_to_total_validation_error(self, inventory_service, mock_repo):
        """Test adding quantity with validation error."""
        # Arrange
        mock_repo.add_quantity.side_effect = ValidationError("Invalid quantity")

        # Act & Assert
        with pytest.raises(ValidationError, match="Invalid quantity"):
            inventory_service.add_to_total(1, -5)

        mock_repo.add_quantity.assert_called_once_with(1, -5)

    def test_get_total_quantity_success(self, inventory_service, mock_repo):
        """Test getting total quantity successfully."""
        # Arrange
        mock_repo.get_quantity.return_value = 25

        # Act
        result = inventory_service.get_total_quantity(1)

        # Assert
        assert result == 25
        mock_repo.get_quantity.assert_called_once_with(1)

    def test_get_total_quantity_not_found(self, inventory_service, mock_repo):
        """Test getting total quantity for non-existent product."""
        # Arrange
        mock_repo.get_quantity.side_effect = EntityNotFoundError("Product not found")

        # Act & Assert
        with pytest.raises(EntityNotFoundError, match="Product not found"):
            inventory_service.get_total_quantity(999)

        mock_repo.get_quantity.assert_called_once_with(999)

    def test_get_all_inventory_success(self, inventory_service, mock_repo):
        """Test getting all inventory successfully."""
        # Arrange
        mock_inventory = [
            {"product_id": 1, "quantity": 10},
            {"product_id": 2, "quantity": 5}
        ]
        mock_repo.get_all.return_value = mock_inventory

        # Act
        result = inventory_service.get_all_inventory()

        # Assert
        assert result == mock_inventory
        mock_repo.get_all.assert_called_once()