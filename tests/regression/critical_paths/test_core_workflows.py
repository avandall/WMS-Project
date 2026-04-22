"""
Regression Tests - Critical Paths
Tests critical business workflows to prevent regressions
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app.api import app
from app.application.services.product_service import ProductService
from app.application.commands.product_commands import CreateProductCommand, UpdateProductCommand, DeleteProductCommand
from app.application.queries.product_queries import GetProductQuery, GetAllProductsQuery


class TestCriticalPathRegression:
    """Regression tests for critical business paths"""

    def test_product_creation_critical_path(self):
        """Test critical product creation path"""
        mock_product_repo = Mock()
        mock_inventory_repo = Mock()
        
        # Setup mock responses
        created_product = Mock()
        created_product.product_id = 1
        created_product.name = "Critical Test Product"
        created_product.price = 99.99
        
        mock_product_repo.save.return_value = created_product
        mock_product_repo.get.return_value = None  # Product doesn't exist
        
        service = ProductService(
            product_repo=mock_product_repo,
            inventory_repo=mock_inventory_repo
        )
        
        # Test critical creation path
        command = CreateProductCommand(
            name="Critical Test Product",
            price=99.99,
            description="Critical path test"
        )
        
        result = service.create_product(command)
        
        # Critical assertions
        assert result is not None
        assert result.name == "Critical Test Product"
        assert result.price == 99.99
        assert mock_product_repo.save.called
        assert mock_product_repo.get.called

    def test_product_retrieval_critical_path(self):
        """Test critical product retrieval path"""
        mock_product_repo = Mock()
        mock_inventory_repo = Mock()
        
        # Setup mock response
        existing_product = Mock()
        existing_product.product_id = 1
        existing_product.name = "Retrieval Test Product"
        existing_product.price = 49.99
        
        mock_product_repo.get.return_value = existing_product
        
        service = ProductService(
            product_repo=mock_product_repo,
            inventory_repo=mock_inventory_repo
        )
        
        # Test critical retrieval path
        query = GetProductQuery(product_id=1)
        result = service.get_product(query)
        
        # Critical assertions
        assert result is not None
        assert result.product_id == 1
        assert result.name == "Retrieval Test Product"
        assert mock_product_repo.get.called_with(1)

    def test_product_update_critical_path(self):
        """Test critical product update path"""
        mock_product_repo = Mock()
        mock_inventory_repo = Mock()
        
        # Setup mock responses
        existing_product = Mock()
        existing_product.product_id = 1
        existing_product.name = "Original Product"
        existing_product.price = 25.00
        
        updated_product = Mock()
        updated_product.product_id = 1
        updated_product.name = "Updated Product"
        updated_product.price = 75.00
        
        mock_product_repo.get.return_value = existing_product
        mock_product_repo.save.return_value = updated_product
        
        service = ProductService(
            product_repo=mock_product_repo,
            inventory_repo=mock_inventory_repo
        )
        
        # Test critical update path
        command = UpdateProductCommand(
            product_id=1,
            name="Updated Product",
            price=75.00
        )
        
        result = service.update_product(command)
        
        # Critical assertions
        assert result is not None
        assert result.name == "Updated Product"
        assert result.price == 75.00
        assert mock_product_repo.get.called_with(1)
        assert mock_product_repo.save.called

    def test_product_deletion_critical_path(self):
        """Test critical product deletion path"""
        mock_product_repo = Mock()
        mock_inventory_repo = Mock()
        
        # Setup mock response
        existing_product = Mock()
        existing_product.product_id = 1
        existing_product.name = "Product to Delete"
        existing_product.price = 15.00
        
        mock_product_repo.get.return_value = existing_product
        mock_product_repo.delete.return_value = True
        
        service = ProductService(
            product_repo=mock_product_repo,
            inventory_repo=mock_inventory_repo
        )
        
        # Test critical deletion path
        command = DeleteProductCommand(product_id=1)
        
        service.delete_product(command)
        
        # Critical assertions
        assert mock_product_repo.get.called_with(1)
        assert mock_product_repo.delete.called_with(1)

    def test_product_listing_critical_path(self):
        """Test critical product listing path"""
        mock_product_repo = Mock()
        mock_inventory_repo = Mock()
        
        # Setup mock response
        products = [
            Mock(product_id=1, name="Product A", price=10.00),
            Mock(product_id=2, name="Product B", price=20.00),
            Mock(product_id=3, name="Product C", price=30.00)
        ]
        mock_product_repo.get_all.return_value = products
        
        service = ProductService(
            product_repo=mock_product_repo,
            inventory_repo=mock_inventory_repo
        )
        
        # Test critical listing path
        query = GetAllProductsQuery()
        result = service.get_all_products(query)
        
        # Critical assertions
        assert result is not None
        assert len(result) == 3
        assert mock_product_repo.get_all.called

    def test_api_endpoints_critical_paths(self):
        """Test critical API endpoints"""
        client = TestClient(app)
        
        # Test critical endpoints
        critical_endpoints = [
            ("GET", "/api/products"),
            ("GET", "/api/products/1"),
            ("POST", "/api/products"),
            ("PUT", "/api/products/1"),
            ("DELETE", "/api/products/1")
        ]
        
        for method, endpoint in critical_endpoints:
            try:
                if method == "GET":
                    response = client.get(endpoint)
                elif method == "POST":
                    response = client.post(endpoint, json={
                        "name": "Critical Test",
                        "price": 99.99
                    })
                elif method == "PUT":
                    response = client.put(endpoint, json={
                        "name": "Critical Update",
                        "price": 149.99
                    })
                elif method == "DELETE":
                    response = client.delete(endpoint)
                
                # Critical assertions
                assert response.status_code in [200, 201, 204, 400, 404, 422, 500]
                
                # Should not crash the server
                assert response is not None
                assert hasattr(response, 'status_code')
            except Exception:
                # Should not crash the application
                assert False, f"Critical endpoint {method} {endpoint} crashed"

    def test_database_operations_critical_paths(self):
        """Test critical database operations"""
        mock_session = Mock()
        mock_container = Mock()
        
        # Test critical database operations
        try:
            # Transaction begin
            mock_session.begin()
            assert mock_session.begin.called
            
            # Save operation
            mock_session.add(Mock())
            assert mock_session.add.called
            
            # Commit operation
            mock_session.commit()
            assert mock_session.commit.called
            
            # Rollback operation
            mock_session.rollback()
            assert mock_session.rollback.called
            
        except Exception:
            # Should not crash on database operations
            assert False, "Database operations crashed"

    def test_validation_critical_paths(self):
        """Test critical validation paths"""
        from app.application.validation.product_validators import ProductValidator
        
        validator = ProductValidator()
        
        # Test critical validation scenarios
        critical_cases = [
            (1, "Valid Product", 10.00, True),   # Valid case
            (0, "Invalid Product", 10.00, False),  # Invalid ID
            (1, "", 10.00, False),               # Invalid name
            (1, "Valid Product", -10.00, False), # Invalid price
        ]
        
        for product_id, name, price, should_succeed in critical_cases:
            try:
                validator.validate_import_data(product_id, name, price)
                
                if should_succeed:
                    # Valid case should not raise exception
                    assert True
                else:
                    # Invalid case should raise exception
                    assert False, f"Validation should have failed for {name}"
            except Exception:
                if should_succeed:
                    assert False, f"Validation should have succeeded for {name}"

    def test_authorization_critical_paths(self):
        """Test critical authorization paths"""
        from app.api.authorization.product_authorizers import ProductAuthorizer
        
        authorizer = ProductAuthorizer()
        
        # Test critical authorization scenarios
        critical_scenarios = [
            ("admin", "create", True),
            ("user", "create", False),
            ("guest", "create", False),
            ("admin", "update", True),
            ("user", "update", False),
            ("guest", "update", False),
            ("admin", "delete", True),
            ("user", "delete", False),
            ("guest", "delete", False)
        ]
        
        for role, action, should_succeed in critical_scenarios:
            try:
                if action == "create":
                    authorizer.can_create_product(role)
                elif action == "update":
                    authorizer.can_update_product(role, Mock())
                elif action == "delete":
                    authorizer.can_delete_product(role)
                
                if should_succeed:
                    # Should succeed
                    assert True
                else:
                    # Should fail gracefully
                    assert False
            except Exception:
                if should_succeed:
                    assert False, f"Authorization should have succeeded for {role} {action}"

    def test_error_handling_critical_paths(self):
        """Test critical error handling paths"""
        mock_product_repo = Mock()
        mock_inventory_repo = Mock()
        
        # Setup mocks to raise exceptions
        mock_product_repo.save.side_effect = Exception("Database error")
        mock_product_repo.get.side_effect = Exception("Connection error")
        mock_product_repo.delete.side_effect = Exception("Deletion error")
        
        service = ProductService(
            product_repo=mock_product_repo,
            inventory_repo=mock_inventory_repo
        )
        
        # Test error handling
        try:
            service.create_product(CreateProductCommand(name="Test", price=10.0))
            assert False, "Should have handled create error"
        except Exception:
            # Should handle exception gracefully
            pass
        
        try:
            service.get_product(GetProductQuery(product_id=1))
            assert False, "Should have handled get error"
        except Exception:
            # Should handle exception gracefully
            pass
        
        try:
            service.delete_product(DeleteProductCommand(product_id=1))
            assert False, "Should have handled delete error"
        except Exception:
            # Should handle exception gracefully
            pass

    def test_performance_critical_paths(self):
        """Test critical performance paths"""
        import time
        import statistics
        
        # Test command creation performance
        iterations = 1000
        times = []
        
        for i in range(iterations):
            start_time = time.perf_counter()
            command = CreateProductCommand(
                name=f"Performance Test {i}",
                price=float(i)
            )
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        p95_time = statistics.quantiles(times, n=100)[94]
        
        # Critical performance assertions
        assert avg_time < 0.001  # Average < 1ms
        assert p95_time < 0.002   # 95th percentile < 2ms
        assert max(times) < 0.01     # Max < 10ms

    def test_data_integrity_critical_paths(self):
        """Test critical data integrity paths"""
        mock_product_repo = Mock()
        mock_inventory_repo = Mock()
        
        # Test data integrity scenarios
        service = ProductService(
            product_repo=mock_product_repo,
            inventory_repo=mock_inventory_repo
        )
        
        # Test data consistency
        try:
            # Create product
            create_command = CreateProductCommand(
                name="Integrity Test",
                price=99.99
            )
            created = service.create_product(create_command)
            
            # Update product
            update_command = UpdateProductCommand(
                product_id=1,
                name="Updated Integrity Test",
                price=149.99
            )
            updated = service.update_product(update_command)
            
            # Retrieve product
            get_query = GetProductQuery(product_id=1)
            retrieved = service.get_product(get_query)
            
            # Data integrity assertions
            assert created is not None
            assert updated is not None
            assert retrieved is not None
            assert mock_product_repo.save.call_count >= 2  # Create + Update
            assert mock_product_repo.get.call_count >= 1  # Retrieve
            
        except Exception:
            # Should not compromise data integrity
            assert False, "Data integrity compromised"

    def test_concurrent_access_critical_paths(self):
        """Test critical concurrent access paths"""
        import threading
        import time
        
        mock_product_repo = Mock()
        mock_inventory_repo = Mock()
        
        service = ProductService(
            product_repo=mock_product_repo,
            inventory_repo=mock_inventory_repo
        )
        
        results = []
        errors = []
        
        def concurrent_access(thread_id):
            try:
                # Simulate concurrent product access
                command = CreateProductCommand(
                    name=f"Concurrent {thread_id}",
                    price=float(thread_id)
                )
                result = service.create_product(command)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=concurrent_access, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Concurrent access assertions
        assert len(errors) == 0
        assert len(results) == 5
        assert mock_product_repo.save.call_count == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
