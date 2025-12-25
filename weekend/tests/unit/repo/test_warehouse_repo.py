"""
Unit tests for WarehouseRepo.
"""

import pytest
from unittest.mock import Mock
from PMKT.repo.warehouse_repo import WarehouseRepo
from PMKT.repo.inventory_repo import InventoryRepo
from PMKT.domain.warehouse_domain import Warehouse
from PMKT.domain.inventory_domain import InventoryItem
from PMKT.module.custom_exceptions import (
    InvalidQuantityError, WarehouseNotFoundError,
    InsufficientStockError, ProductNotFoundError
)


class TestWarehouseRepo:
    """Test cases for WarehouseRepo."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repo = WarehouseRepo()
        self.inventory_repo = InventoryRepo()
        self.repo_with_inventory = WarehouseRepo(inventory_repo=self.inventory_repo)

    def test_create_and_save_warehouse(self):
        """Test creating and saving a warehouse."""
        warehouse = Warehouse(warehouse_id=1, location="Test Location")

        self.repo.create_warehouse(warehouse)
        retrieved = self.repo.get(1)

        assert retrieved is not None
        assert retrieved.warehouse_id == 1
        assert retrieved.location == "Test Location"

    def test_save_warehouse(self):
        """Test saving a warehouse."""
        warehouse = Warehouse(warehouse_id=1, location="Test")

        self.repo.save(warehouse)
        retrieved = self.repo.get(1)

        assert retrieved is not None
        assert retrieved.warehouse_id == 1

    def test_get_nonexistent_warehouse(self):
        """Test getting a warehouse that doesn't exist."""
        result = self.repo.get(999)
        assert result is None

    def test_delete_existing_warehouse(self):
        """Test deleting an existing warehouse."""
        warehouse = Warehouse(warehouse_id=1, location="Test")
        self.repo.save(warehouse)

        self.repo.delete(1)
        assert self.repo.get(1) is None

    def test_delete_nonexistent_warehouse(self):
        """Test deleting a nonexistent warehouse does nothing."""
        # Should not raise an exception
        self.repo.delete(999)

    def test_add_product_to_warehouse_new_product(self):
        """Test adding a new product to warehouse."""
        warehouse = Warehouse(warehouse_id=1, location="Test")
        self.repo.save(warehouse)

        self.repo.add_product_to_warehouse(1, product_id=100, quantity=10)

        warehouse = self.repo.get(1)
        assert len(warehouse.inventory) == 1
        assert warehouse.inventory[0].product_id == 100
        assert warehouse.inventory[0].quantity == 10

    def test_add_product_to_warehouse_existing_product(self):
        """Test adding quantity to existing product in warehouse."""
        warehouse = Warehouse(warehouse_id=1, location="Test")
        warehouse.inventory.append(InventoryItem(product_id=100, quantity=5))
        self.repo.save(warehouse)

        self.repo.add_product_to_warehouse(1, product_id=100, quantity=3)

        warehouse = self.repo.get(1)
        assert len(warehouse.inventory) == 1
        assert warehouse.inventory[0].product_id == 100
        assert warehouse.inventory[0].quantity == 8

    def test_add_product_to_warehouse_invalid_quantity(self):
        """Test adding product with invalid quantity raises InvalidQuantityError."""
        warehouse = Warehouse(warehouse_id=1, location="Test")
        self.repo.save(warehouse)

        with pytest.raises(InvalidQuantityError, match="Quantity must be positive"):
            self.repo.add_product_to_warehouse(1, product_id=100, quantity=0)

        with pytest.raises(InvalidQuantityError, match="Quantity must be positive"):
            self.repo.add_product_to_warehouse(1, product_id=100, quantity=-5)

    def test_add_product_to_nonexistent_warehouse(self):
        """Test adding product to nonexistent warehouse raises WarehouseNotFoundError."""
        with pytest.raises(WarehouseNotFoundError, match="Warehouse 999 not found"):
            self.repo.add_product_to_warehouse(999, product_id=100, quantity=10)

    def test_add_product_with_inventory_repo(self):
        """Test adding product updates total inventory when inventory_repo is set."""
        warehouse = Warehouse(warehouse_id=1, location="Test")
        self.repo_with_inventory.save(warehouse)

        self.repo_with_inventory.add_product_to_warehouse(1, product_id=100, quantity=10)

        # Check total inventory was updated
        assert self.inventory_repo.get_quantity(100) == 10

    def test_remove_product_from_warehouse_existing_product(self):
        """Test removing quantity from existing product in warehouse."""
        warehouse = Warehouse(warehouse_id=1, location="Test")
        warehouse.inventory.append(InventoryItem(product_id=100, quantity=10))
        self.repo.save(warehouse)

        self.repo.remove_product_from_warehouse(1, product_id=100, quantity=3)

        warehouse = self.repo.get(1)
        assert len(warehouse.inventory) == 1
        assert warehouse.inventory[0].product_id == 100
        assert warehouse.inventory[0].quantity == 7

    def test_remove_product_from_warehouse_completely(self):
        """Test removing all quantity of a product from warehouse."""
        warehouse = Warehouse(warehouse_id=1, location="Test")
        warehouse.inventory.append(InventoryItem(product_id=100, quantity=5))
        self.repo.save(warehouse)

        self.repo.remove_product_from_warehouse(1, product_id=100, quantity=5)

        warehouse = self.repo.get(1)
        assert len(warehouse.inventory) == 0

    def test_remove_product_from_warehouse_insufficient_stock(self):
        """Test removing more quantity than available raises InsufficientStockError."""
        warehouse = Warehouse(warehouse_id=1, location="Test")
        warehouse.inventory.append(InventoryItem(product_id=100, quantity=5))
        self.repo.save(warehouse)

        with pytest.raises(InsufficientStockError, match="Insufficient stock for product 100"):
            self.repo.remove_product_from_warehouse(1, product_id=100, quantity=10)

    def test_remove_product_from_warehouse_nonexistent_product(self):
        """Test removing nonexistent product from warehouse raises ProductNotFoundError."""
        warehouse = Warehouse(warehouse_id=1, location="Test")
        self.repo.save(warehouse)

        with pytest.raises(ProductNotFoundError, match="Product 100 not found in warehouse 1"):
            self.repo.remove_product_from_warehouse(1, product_id=100, quantity=5)

    def test_remove_product_from_warehouse_invalid_quantity(self):
        """Test removing product with invalid quantity raises InvalidQuantityError."""
        warehouse = Warehouse(warehouse_id=1, location="Test")
        warehouse.inventory.append(InventoryItem(product_id=100, quantity=10))
        self.repo.save(warehouse)

        with pytest.raises(InvalidQuantityError, match="Quantity must be positive"):
            self.repo.remove_product_from_warehouse(1, product_id=100, quantity=0)

    def test_remove_product_from_nonexistent_warehouse(self):
        """Test removing product from nonexistent warehouse raises WarehouseNotFoundError."""
        with pytest.raises(WarehouseNotFoundError, match="Warehouse 999 not found"):
            self.repo.remove_product_from_warehouse(999, product_id=100, quantity=5)

    def test_remove_product_with_inventory_repo(self):
        """Test removing product updates total inventory when inventory_repo is set."""
        warehouse = Warehouse(warehouse_id=1, location="Test")
        warehouse.inventory.append(InventoryItem(product_id=100, quantity=10))
        self.repo_with_inventory.save(warehouse)

        # First add to inventory
        self.inventory_repo.add_quantity(100, 10)

        self.repo_with_inventory.remove_product_from_warehouse(1, product_id=100, quantity=3)

        # Check total inventory was updated
        assert self.inventory_repo.get_quantity(100) == 7

    def test_get_warehouse_inventory_existing_warehouse(self):
        """Test getting inventory for existing warehouse."""
        warehouse = Warehouse(warehouse_id=1, location="Test")
        warehouse.inventory.append(InventoryItem(product_id=100, quantity=10))
        warehouse.inventory.append(InventoryItem(product_id=200, quantity=5))
        self.repo.save(warehouse)

        inventory = self.repo.get_warehouse_inventory(1)
        assert len(inventory) == 2
        assert inventory[0].product_id == 100
        assert inventory[0].quantity == 10
        assert inventory[1].product_id == 200
        assert inventory[1].quantity == 5

    def test_get_warehouse_inventory_empty_warehouse(self):
        """Test getting inventory for warehouse with no products."""
        warehouse = Warehouse(warehouse_id=1, location="Test")
        self.repo.save(warehouse)

        inventory = self.repo.get_warehouse_inventory(1)
        assert len(inventory) == 0

    def test_get_warehouse_inventory_nonexistent_warehouse(self):
        """Test getting inventory for nonexistent warehouse returns empty list."""
        inventory = self.repo.get_warehouse_inventory(999)
        assert inventory == []