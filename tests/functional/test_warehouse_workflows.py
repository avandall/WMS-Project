"""
Functional tests for warehouse management workflows.
Tests complete end-to-end business processes using services directly.
"""

import pytest
from PMKT.services.product_service import ProductService
from PMKT.services.warehouse_service import WarehouseService
from PMKT.services.inventory_service import InventoryService
from PMKT.services.document_service import DocumentService
from PMKT.repo.product_repo import ProductRepo
from PMKT.repo.warehouse_repo import WarehouseRepo
from PMKT.repo.inventory_repo import InventoryRepo
from PMKT.repo.document_repo import DocumentRepo
from PMKT.domain.document_domain import DocumentType, DocumentProduct
from PMKT.module.custom_exceptions import ValidationError, InvalidQuantityError


class TestWarehouseManagementWorkflow:
    """Functional tests for complete warehouse management workflows."""

    def setup_method(self):
        """Set up test fixtures with real repositories and services."""
        # Create repositories
        self.product_repo = ProductRepo()
        self.inventory_repo = InventoryRepo()
        self.warehouse_repo = WarehouseRepo(self.inventory_repo)
        self.document_repo = DocumentRepo()

        # Create services
        self.product_service = ProductService(self.product_repo)
        self.inventory_service = InventoryService(self.inventory_repo)
        self.warehouse_service = WarehouseService(self.warehouse_repo)
        self.document_service = DocumentService(self.document_repo, self.warehouse_service)

    def test_product_lifecycle_workflow(self):
        """Test complete product lifecycle: create, update, use in transactions, delete."""
        # Create product
        product = self.product_service.create_product(
            product_id=1,
            name="Functional Test Product",
            price=100.0,
            description="Product for functional testing"
        )
        assert product.product_id == 1
        assert product.name == "Functional Test Product"

        # Update product
        updated_product = self.product_service.update(
            product_id=1,
            name="Updated Functional Product",
            price=120.0
        )
        assert updated_product.name == "Updated Functional Product"
        assert updated_product.price == 120.0

        # Get product details
        retrieved_product = self.product_service.get_product_details(1)
        assert retrieved_product.price == 120.0

        # Use product in warehouse operations (will be tested in other workflows)

        # Delete product
        self.product_service.delete_product(1)

        # Verify product is gone
        with pytest.raises(KeyError):
            self.product_service.get_product_details(1)

    def test_warehouse_inventory_management_workflow(self):
        """Test warehouse creation and inventory management workflow."""
        # Create warehouse
        warehouse = self.warehouse_service.create_warehouse("Functional Test Warehouse")
        warehouse_id = warehouse.warehouse_id

        # Create product
        product = self.product_service.create_product(
            product_id=2,
            name="Inventory Test Product",
            price=50.0
        )

        # Initially empty inventory
        inventory = self.warehouse_service.get_warehouse_inventory(warehouse_id)
        assert len(inventory) == 0

        # Add product to warehouse
        self.warehouse_service.add_product_to_warehouse(
            warehouse_id=warehouse_id,
            product_id=2,
            quantity=100
        )

        # Check inventory
        inventory = self.warehouse_service.get_warehouse_inventory(warehouse_id)
        assert len(inventory) == 1
        assert inventory[0].product_id == 2
        assert inventory[0].quantity == 100

        # Add more of the same product
        self.warehouse_service.add_product_to_warehouse(
            warehouse_id=warehouse_id,
            product_id=2,
            quantity=50
        )

        inventory = self.warehouse_service.get_warehouse_inventory(warehouse_id)
        assert inventory[0].quantity == 150

        # Remove some product
        self.warehouse_service.remove_product_from_warehouse(
            warehouse_id=warehouse_id,
            product_id=2,
            quantity=75
        )

        inventory = self.warehouse_service.get_warehouse_inventory(warehouse_id)
        assert inventory[0].quantity == 75

        # Remove remaining product
        self.warehouse_service.remove_product_from_warehouse(
            warehouse_id=warehouse_id,
            product_id=2,
            quantity=75
        )

        inventory = self.warehouse_service.get_warehouse_inventory(warehouse_id)
        assert len(inventory) == 0

    def test_import_document_workflow(self):
        """Test complete import document workflow."""
        # Create warehouse and product
        warehouse = self.warehouse_service.create_warehouse("Import Test Warehouse")
        warehouse_id = warehouse.warehouse_id

        product = self.product_service.create_product(
            product_id=3,
            name="Import Test Product",
            price=75.0
        )

        # Create import document
        items = [
            DocumentProduct(product_id=3, quantity=200, unit_price=75.0)
        ]

        document = self.document_service.create_import_document(
            to_warehouse_id=warehouse_id,
            items=items,
            created_by="functional_test_user"
        )

        assert document.doc_type == DocumentType.IMPORT
        assert document.to_warehouse_id == warehouse_id
        assert len(document.items) == 1
        assert document.status.name == "DRAFT"

        # Post the document (this would typically trigger inventory updates)
        # Note: The document service might need additional implementation for posting

        # Verify document exists
        retrieved_doc = self.document_service.get_document(document.document_id)
        assert retrieved_doc.document_id == document.document_id

    def test_export_document_workflow(self):
        """Test complete export document workflow."""
        # Create warehouse and add product to it
        warehouse = self.warehouse_service.create_warehouse("Export Test Warehouse")
        warehouse_id = warehouse.warehouse_id

        product = self.product_service.create_product(
            product_id=4,
            name="Export Test Product",
            price=60.0
        )

        # Add product to warehouse
        self.warehouse_service.add_product_to_warehouse(
            warehouse_id=warehouse_id,
            product_id=4,
            quantity=100
        )

        # Create export document
        items = [
            DocumentProduct(product_id=4, quantity=30, unit_price=60.0)
        ]

        document = self.document_service.create_export_document(
            from_warehouse_id=warehouse_id,
            items=items,
            created_by="functional_test_user"
        )

        assert document.doc_type == DocumentType.EXPORT
        assert document.from_warehouse_id == warehouse_id
        assert len(document.items) == 1
        assert document.status.name == "DRAFT"

    def test_transfer_document_workflow(self):
        """Test complete transfer document workflow."""
        # Create two warehouses
        source_warehouse = self.warehouse_service.create_warehouse("Source Warehouse")
        dest_warehouse = self.warehouse_service.create_warehouse("Destination Warehouse")
        source_id = source_warehouse.warehouse_id
        dest_id = dest_warehouse.warehouse_id

        # Create product and add to source warehouse
        product = self.product_service.create_product(
            product_id=5,
            name="Transfer Test Product",
            price=80.0
        )

        self.warehouse_service.add_product_to_warehouse(
            warehouse_id=source_id,
            product_id=5,
            quantity=150
        )

        # Create transfer document
        items = [
            DocumentProduct(product_id=5, quantity=75, unit_price=80.0)
        ]

        document = self.document_service.create_transfer_document(
            from_warehouse_id=source_id,
            to_warehouse_id=dest_id,
            items=items,
            created_by="functional_test_user"
        )

        assert document.doc_type == DocumentType.TRANSFER
        assert document.from_warehouse_id == source_id
        assert document.to_warehouse_id == dest_id
        assert len(document.items) == 1
        assert document.status.name == "DRAFT"

    def test_insufficient_stock_prevention(self):
        """Test that operations prevent insufficient stock situations."""
        # Create warehouse and product
        warehouse = self.warehouse_service.create_warehouse("Stock Control Warehouse")
        warehouse_id = warehouse.warehouse_id

        product = self.product_service.create_product(
            product_id=6,
            name="Stock Control Product",
            price=90.0
        )

        # Add limited quantity
        self.warehouse_service.add_product_to_warehouse(
            warehouse_id=warehouse_id,
            product_id=6,
            quantity=50
        )

        # Try to create export document with more than available
        items = [
            DocumentProduct(product_id=6, quantity=75, unit_price=90.0)  # More than available
        ]

        # This should succeed at document level (documents can be created for future stock)
        document = self.document_service.create_export_document(
            from_warehouse_id=warehouse_id,
            items=items,
            created_by="test_user"
        )
        assert document is not None

        # But trying to remove more than available from warehouse should fail
        with pytest.raises(Exception):  # Could be InsufficientStockError or similar
            self.warehouse_service.remove_product_from_warehouse(
                warehouse_id=warehouse_id,
                product_id=6,
                quantity=75  # More than the 50 available
            )

    def test_multiple_warehouses_inventory_tracking(self):
        """Test inventory tracking across multiple warehouses."""
        # Create multiple warehouses
        warehouse1 = self.warehouse_service.create_warehouse("Warehouse 1")
        warehouse2 = self.warehouse_service.create_warehouse("Warehouse 2")
        w1_id = warehouse1.warehouse_id
        w2_id = warehouse2.warehouse_id

        # Create product
        product = self.product_service.create_product(
            product_id=7,
            name="Multi-Warehouse Product",
            price=45.0
        )

        # Add to warehouse 1
        self.warehouse_service.add_product_to_warehouse(w1_id, 7, 100)

        # Add to warehouse 2
        self.warehouse_service.add_product_to_warehouse(w2_id, 7, 200)

        # Check individual warehouse inventories
        w1_inventory = self.warehouse_service.get_warehouse_inventory(w1_id)
        w2_inventory = self.warehouse_service.get_warehouse_inventory(w2_id)

        assert len(w1_inventory) == 1
        assert w1_inventory[0].quantity == 100
        assert len(w2_inventory) == 1
        assert w2_inventory[0].quantity == 200

        # Total inventory should be tracked separately
        # (This would require additional service methods to aggregate)

    def test_business_rules_enforcement(self):
        """Test that business rules are properly enforced across the system."""
        # Test warehouse location requirements
        with pytest.raises(ValidationError):
            self.warehouse_service.create_warehouse("")  # Empty location

        # Test product validation
        with pytest.raises(ValidationError):
            self.product_service.create_product(
                product_id=8,
                name="",  # Empty name
                price=10.0
            )

        with pytest.raises(InvalidQuantityError):
            self.product_service.create_product(
                product_id=9,
                name="Valid Name",
                price=-5.0  # Negative price
            )

        # Test quantity validations
        warehouse = self.warehouse_service.create_warehouse("Rules Test Warehouse")
        product = self.product_service.create_product(10, "Rules Product", 25.0)

        with pytest.raises(Exception):  # InvalidQuantityError
            self.warehouse_service.add_product_to_warehouse(
                warehouse_id=warehouse.warehouse_id,
                product_id=10,
                quantity=-10  # Negative quantity
            )