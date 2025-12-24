"""
Integration tests for Warehouses API endpoints.
Tests warehouse creation, inventory management, and product movements.
"""

import pytest
from fastapi.testclient import TestClient
from PMKT.api import app


class TestWarehousesAPI:
    """Integration tests for Warehouses API."""

    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)

    def test_create_warehouse_success(self):
        """Test creating a warehouse successfully."""
        warehouse_data = {"location": "Test Warehouse Location"}

        response = self.client.post("/api/v1/warehouses/", json=warehouse_data)

        assert response.status_code == 200
        data = response.json()
        assert "warehouse_id" in data
        assert data["location"] == "Test Warehouse Location"
        assert data["inventory"] == []

        # Store warehouse ID for other tests
        self.warehouse_id = data["warehouse_id"]

    def test_get_warehouse_inventory(self):
        """Test getting warehouse inventory."""
        # First create a warehouse
        warehouse_data = {"location": "Inventory Test Warehouse"}
        response = self.client.post("/api/v1/warehouses/", json=warehouse_data)
        warehouse_id = response.json()["warehouse_id"]

        # Get warehouse inventory (should be empty)
        response = self.client.get(f"/api/v1/warehouses/{warehouse_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["warehouse_id"] == warehouse_id
        assert data["inventory"] == []

    def test_get_nonexistent_warehouse(self):
        """Test getting a nonexistent warehouse."""
        response = self.client.get("/api/v1/warehouses/999")

        assert response.status_code == 404

    def test_add_product_to_warehouse(self):
        """Test adding product to warehouse."""
        # Create warehouse
        warehouse_data = {"location": "Add Product Warehouse"}
        response = self.client.post("/api/v1/warehouses/", json=warehouse_data)
        warehouse_id = response.json()["warehouse_id"]

        # Create product first
        product_data = {
            "product_id": 100,
            "name": "Warehouse Test Product",
            "price": 25.0
        }
        self.client.post("/api/v1/products/", json=product_data)

        # Add product to warehouse
        movement_data = {
            "product_id": 100,
            "quantity": 50
        }
        response = self.client.post(f"/api/v1/warehouses/{warehouse_id}/products", json=movement_data)

        assert response.status_code == 200
        data = response.json()
        assert "Added 50 of product 100" in data["message"]

        # Verify product was added
        response = self.client.get(f"/api/v1/warehouses/{warehouse_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["inventory"]) == 1
        assert data["inventory"][0]["product_id"] == 100
        assert data["inventory"][0]["quantity"] == 50

    def test_add_product_to_nonexistent_warehouse(self):
        """Test adding product to nonexistent warehouse."""
        movement_data = {
            "product_id": 100,
            "quantity": 10
        }
        response = self.client.post("/api/v1/warehouses/999/products", json=movement_data)

        assert response.status_code == 400

    def test_add_invalid_quantity_to_warehouse(self):
        """Test adding invalid quantity to warehouse."""
        # Create warehouse
        warehouse_data = {"location": "Invalid Quantity Warehouse"}
        response = self.client.post("/api/v1/warehouses/", json=warehouse_data)
        warehouse_id = response.json()["warehouse_id"]

        # Try to add negative quantity
        movement_data = {
            "product_id": 100,
            "quantity": -5
        }
        response = self.client.post(f"/api/v1/warehouses/{warehouse_id}/products", json=movement_data)

        assert response.status_code == 422

    def test_add_more_product_to_existing_inventory(self):
        """Test adding more quantity to existing product in warehouse."""
        # Create warehouse and product
        warehouse_data = {"location": "Existing Inventory Warehouse"}
        response = self.client.post("/api/v1/warehouses/", json=warehouse_data)
        warehouse_id = response.json()["warehouse_id"]

        product_data = {
            "product_id": 200,
            "name": "Existing Inventory Product",
            "price": 30.0
        }
        self.client.post("/api/v1/products/", json=product_data)

        # Add initial quantity
        movement_data = {
            "product_id": 200,
            "quantity": 20
        }
        self.client.post(f"/api/v1/warehouses/{warehouse_id}/products", json=movement_data)

        # Add more quantity
        movement_data = {
            "product_id": 200,
            "quantity": 15
        }
        response = self.client.post(f"/api/v1/warehouses/{warehouse_id}/products", json=movement_data)

        assert response.status_code == 200

        # Verify total quantity
        response = self.client.get(f"/api/v1/warehouses/{warehouse_id}")
        data = response.json()
        assert len(data["inventory"]) == 1
        assert data["inventory"][0]["quantity"] == 35

    def test_remove_product_from_warehouse(self):
        """Test removing product from warehouse."""
        # Create warehouse, product, and add to inventory
        warehouse_data = {"location": "Remove Product Warehouse"}
        response = self.client.post("/api/v1/warehouses/", json=warehouse_data)
        warehouse_id = response.json()["warehouse_id"]

        product_data = {
            "product_id": 300,
            "name": "Remove Test Product",
            "price": 40.0
        }
        self.client.post("/api/v1/products/", json=product_data)

        # Add product to warehouse
        movement_data = {
            "product_id": 300,
            "quantity": 25
        }
        self.client.post(f"/api/v1/warehouses/{warehouse_id}/products", json=movement_data)

        # Remove some quantity
        movement_data = {
            "product_id": 300,
            "quantity": 10
        }
        response = self.client.request("DELETE", f"/api/v1/warehouses/{warehouse_id}/products", json=movement_data)

        assert response.status_code == 200
        data = response.json()
        assert "Removed 10 of product 300" in data["message"]

        # Verify remaining quantity
        response = self.client.get(f"/api/v1/warehouses/{warehouse_id}")
        data = response.json()
        assert data["inventory"][0]["quantity"] == 15

    def test_remove_all_product_from_warehouse(self):
        """Test removing all quantity of a product from warehouse."""
        # Create warehouse, product, and add to inventory
        warehouse_data = {"location": "Remove All Warehouse"}
        response = self.client.post("/api/v1/warehouses/", json=warehouse_data)
        warehouse_id = response.json()["warehouse_id"]

        product_data = {
            "product_id": 400,
            "name": "Remove All Product",
            "price": 50.0
        }
        self.client.post("/api/v1/products/", json=product_data)

        # Add product to warehouse
        movement_data = {
            "product_id": 400,
            "quantity": 10
        }
        self.client.post(f"/api/v1/warehouses/{warehouse_id}/products", json=movement_data)

        # Remove all quantity
        movement_data = {
            "product_id": 400,
            "quantity": 10
        }
        response = self.client.request("DELETE", f"/api/v1/warehouses/{warehouse_id}/products", json=movement_data)

        assert response.status_code == 200

        # Verify product is completely removed
        response = self.client.get(f"/api/v1/warehouses/{warehouse_id}")
        data = response.json()
        assert len(data["inventory"]) == 0

    def test_remove_insufficient_stock_from_warehouse(self):
        """Test removing more quantity than available from warehouse."""
        # Create warehouse, product, and add to inventory
        warehouse_data = {"location": "Insufficient Stock Warehouse"}
        response = self.client.post("/api/v1/warehouses/", json=warehouse_data)
        warehouse_id = response.json()["warehouse_id"]

        product_data = {
            "product_id": 500,
            "name": "Insufficient Stock Product",
            "price": 60.0
        }
        self.client.post("/api/v1/products/", json=product_data)

        # Add limited quantity
        movement_data = {
            "product_id": 500,
            "quantity": 5
        }
        self.client.post(f"/api/v1/warehouses/{warehouse_id}/products", json=movement_data)

        # Try to remove more than available
        movement_data = {
            "product_id": 500,
            "quantity": 10
        }
        response = self.client.request("DELETE", f"/api/v1/warehouses/{warehouse_id}/products", json=movement_data)

        assert response.status_code == 400

    def test_remove_product_not_in_warehouse(self):
        """Test removing product that doesn't exist in warehouse."""
        # Create warehouse
        warehouse_data = {"location": "No Product Warehouse"}
        response = self.client.post("/api/v1/warehouses/", json=warehouse_data)
        warehouse_id = response.json()["warehouse_id"]

        # Try to remove product not in warehouse
        movement_data = {
            "product_id": 600,
            "quantity": 5
        }
        response = self.client.request("DELETE", f"/api/v1/warehouses/{warehouse_id}/products", json=movement_data)

        assert response.status_code == 400

    def test_warehouse_inventory_workflow(self):
        """Test complete warehouse inventory workflow."""
        # Create warehouse and product
        warehouse_data = {"location": "Workflow Warehouse"}
        response = self.client.post("/api/v1/warehouses/", json=warehouse_data)
        warehouse_id = response.json()["warehouse_id"]

        product_data = {
            "product_id": 700,
            "name": "Workflow Product",
            "price": 75.0
        }
        self.client.post("/api/v1/products/", json=product_data)

        # Initially empty
        response = self.client.get(f"/api/v1/warehouses/{warehouse_id}")
        assert len(response.json()["inventory"]) == 0

        # Add products
        movement_data = {"product_id": 700, "quantity": 100}
        self.client.post(f"/api/v1/warehouses/{warehouse_id}/products", json=movement_data)

        response = self.client.get(f"/api/v1/warehouses/{warehouse_id}")
        assert response.json()["inventory"][0]["quantity"] == 100

        # Add more
        movement_data = {"product_id": 700, "quantity": 50}
        self.client.post(f"/api/v1/warehouses/{warehouse_id}/products", json=movement_data)

        response = self.client.get(f"/api/v1/warehouses/{warehouse_id}")
        assert response.json()["inventory"][0]["quantity"] == 150

        # Remove some
        movement_data = {"product_id": 700, "quantity": 75}
        self.client.request("DELETE", f"/api/v1/warehouses/{warehouse_id}/products", json=movement_data)

        response = self.client.get(f"/api/v1/warehouses/{warehouse_id}")
        assert response.json()["inventory"][0]["quantity"] == 75