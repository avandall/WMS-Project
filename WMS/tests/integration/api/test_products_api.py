"""
Integration tests for Products API endpoints.
Tests the complete request/response cycle including FastAPI routing and service layer.
"""

import pytest
from httpx import AsyncClient
from app.api import app
from app.api.schemas.product import ProductCreate, ProductUpdate


class TestProductsAPI:
    """Integration tests for Products API."""

    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)

    def test_create_product_success(self):
        """Test creating a product successfully."""
        product_data = {
            "product_id": 1,
            "name": "Test Product",
            "price": 29.99,
            "description": "A test product"
        }

        response = self.client.post("/api/v1/products/", json=product_data)

        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == 1
        assert data["name"] == "Test Product"
        assert data["price"] == 29.99
        assert data["description"] == "A test product"

    def test_create_product_without_description(self):
        """Test creating a product without description."""
        product_data = {
            "product_id": 2,
            "name": "Product No Desc",
            "price": 19.99
        }

        response = self.client.post("/api/v1/products/", json=product_data)

        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == 2
        assert data["description"] is None

    def test_create_product_invalid_data(self):
        """Test creating a product with invalid data."""
        # Test empty name
        product_data = {
            "product_id": 3,
            "name": "",
            "price": 10.0
        }

        response = self.client.post("/api/v1/products/", json=product_data)
        assert response.status_code == 422

    def test_get_product_success(self):
        """Test getting a product successfully."""
        # First create a product
        product_data = {
            "product_id": 4,
            "name": "Get Test Product",
            "price": 39.99
        }
        self.client.post("/api/v1/products/", json=product_data)

        # Then get it
        response = self.client.get("/api/v1/products/4")

        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == 4
        assert data["name"] == "Get Test Product"
        assert data["price"] == 39.99

    def test_get_product_not_found(self):
        """Test getting a nonexistent product."""
        response = self.client.get("/api/v1/products/999")

        assert response.status_code == 404

    def test_update_product_success(self):
        """Test updating a product successfully."""
        # Create product
        product_data = {
            "product_id": 5,
            "name": "Original Name",
            "price": 20.0,
            "description": "Original desc"
        }
        self.client.post("/api/v1/products/", json=product_data)

        # Update it
        update_data = {
            "name": "Updated Name",
            "price": 25.0,
            "description": "Updated desc"
        }
        response = self.client.put("/api/v1/products/5", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["price"] == 25.0
        assert data["description"] == "Updated desc"

    def test_update_product_partial(self):
        """Test updating only some fields of a product."""
        # Create product
        product_data = {
            "product_id": 6,
            "name": "Partial Update",
            "price": 30.0,
            "description": "Original desc"
        }
        self.client.post("/api/v1/products/", json=product_data)

        # Update only price
        update_data = {"price": 35.0}
        response = self.client.put("/api/v1/products/6", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Partial Update"  # Unchanged
        assert data["price"] == 35.0  # Changed
        assert data["description"] == "Original desc"  # Unchanged

    def test_update_product_not_found(self):
        """Test updating a nonexistent product."""
        update_data = {"name": "New Name"}
        response = self.client.put("/api/v1/products/999", json=update_data)

        assert response.status_code == 404

    def test_update_product_invalid_data(self):
        """Test updating a product with invalid data."""
        # Create valid product
        product_data = {
            "product_id": 7,
            "name": "Valid Product",
            "price": 10.0
        }
        self.client.post("/api/v1/products/", json=product_data)

        # Try to update with invalid data
        update_data = {"name": ""}  # Empty name
        response = self.client.put("/api/v1/products/7", json=update_data)

        assert response.status_code == 422

    def test_delete_product_success(self):
        """Test deleting a product successfully."""
        # Create product
        product_data = {
            "product_id": 8,
            "name": "Delete Test",
            "price": 15.0
        }
        self.client.post("/api/v1/products/", json=product_data)

        # Delete it
        response = self.client.delete("/api/v1/products/8")

        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"]

        # Verify it's gone
        response = self.client.get("/api/v1/products/8")
        assert response.status_code == 404

    def test_delete_product_not_found(self):
        """Test deleting a nonexistent product."""
        response = self.client.delete("/api/v1/products/999")

        assert response.status_code == 404

    def test_product_workflow(self):
        """Test complete product workflow: create, read, update, delete."""
        product_id = 9

        # Create
        product_data = {
            "product_id": product_id,
            "name": "Workflow Product",
            "price": 50.0,
            "description": "Testing workflow"
        }
        response = self.client.post("/api/v1/products/", json=product_data)
        assert response.status_code == 200

        # Read
        response = self.client.get(f"/api/v1/products/{product_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Workflow Product"

        # Update
        update_data = {"name": "Updated Workflow Product", "price": 55.0}
        response = self.client.put(f"/api/v1/products/{product_id}", json=update_data)
        assert response.status_code == 200

        # Verify update
        response = self.client.get(f"/api/v1/products/{product_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Workflow Product"
        assert data["price"] == 55.0

        # Delete
        response = self.client.delete(f"/api/v1/products/{product_id}")
        assert response.status_code == 200

        # Verify deletion
        response = self.client.get(f"/api/v1/products/{product_id}")
        assert response.status_code == 404