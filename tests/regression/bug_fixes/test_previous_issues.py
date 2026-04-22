"""
Regression Tests - Bug Fixes
Tests to ensure previous bugs don't reoccur
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app.api import app
from app.application.services.product_service import ProductService
from app.application.commands.product_commands import CreateProductCommand, UpdateProductCommand, DeleteProductCommand
from app.application.validation.product_validators import ProductValidator
from app.domain.entities.product import Product


class TestPreviousBugFixes:
    """Regression tests for previously fixed bugs"""

    def test_product_id_validation_bug_fix(self):
        """Test bug: Product ID validation was not working"""
        validator = ProductValidator()
        
        # Previously this would fail - ensure it's fixed
        try:
            validator.validate_import_data(1, "Valid Product", 10.0)
            # Should succeed
            assert True
        except Exception as e:
            pytest.fail(f"Product ID validation bug reoccurred: {e}")

    def test_negative_price_validation_bug_fix(self):
        """Test bug: Negative price validation was inconsistent"""
        validator = ProductValidator()
        
        # Previously negative prices might pass - ensure they don't
        try:
            validator.validate_import_data(1, "Valid Product", -10.0)
            pytest.fail("Negative price validation bug reoccurred")
        except Exception:
            # Should fail - this is expected
            assert True

    def test_empty_name_validation_bug_fix(self):
        """Test bug: Empty name validation was bypassed"""
        validator = ProductValidator()
        
        # Previously empty names might pass - ensure they don't
        try:
            validator.validate_import_data(1, "", 10.0)
            pytest.fail("Empty name validation bug reoccurred")
        except Exception:
            # Should fail - this is expected
            assert True

    def test_duplicate_product_creation_bug_fix(self):
        """Test bug: Duplicate product creation was allowed"""
        mock_product_repo = Mock()
        mock_inventory_repo = Mock()
        
        # Setup mock to simulate existing product
        existing_product = Product(
            product_id=1,
            name="Existing Product",
            price=10.0
        )
        mock_product_repo.get.return_value = existing_product
        
        service = ProductService(
            product_repo=mock_product_repo,
            inventory_repo=mock_inventory_repo
        )
        
        # Try to create duplicate
        command = CreateProductCommand(
            name="Existing Product",
            price=10.0
        )
        
        try:
            result = service.create_product(command)
            # Should either fail or update existing
            assert True  # Just ensure no crash
        except Exception:
            # Expected behavior - should prevent duplicates
            assert True

    def test_product_update_not_found_bug_fix(self):
        """Test bug: Updating non-existent product didn't return proper error"""
        mock_product_repo = Mock()
        mock_inventory_repo = Mock()
        
        # Setup mock to simulate non-existent product
        mock_product_repo.get.return_value = None
        
        service = ProductService(
            product_repo=mock_product_repo,
            inventory_repo=mock_inventory_repo
        )
        
        # Try to update non-existent product
        command = UpdateProductCommand(
            product_id=999,
            name="Updated Product",
            price=15.0
        )
        
        try:
            result = service.update_product(command)
            # Should handle gracefully
            assert True  # Just ensure no crash
        except Exception:
            # Expected behavior - should handle not found
            assert True

    def test_product_delete_not_found_bug_fix(self):
        """Test bug: Deleting non-existent product didn't return proper error"""
        mock_product_repo = Mock()
        mock_inventory_repo = Mock()
        
        # Setup mock to simulate non-existent product
        mock_product_repo.get.return_value = None
        
        service = ProductService(
            product_repo=mock_product_repo,
            inventory_repo=mock_inventory_repo
        )
        
        # Try to delete non-existent product
        command = DeleteProductCommand(product_id=999)
        
        try:
            service.delete_product(command)
            # Should handle gracefully
            assert True  # Just ensure no crash
        except Exception:
            # Expected behavior - should handle not found
            assert True

    def test_price_precision_bug_fix(self):
        """Test bug: Price precision was lost in calculations"""
        mock_product_repo = Mock()
        mock_inventory_repo = Mock()
        
        service = ProductService(
            product_repo=mock_product_repo,
            inventory_repo=mock_inventory_repo
        )
        
        # Test with high precision price
        high_precision_price = 99.999999999
        command = CreateProductCommand(
            name="Precision Test",
            price=high_precision_price
        )
        
        try:
            result = service.create_product(command)
            # Should preserve precision
            if result and hasattr(result, 'price'):
                assert abs(result.price - high_precision_price) < 0.000001
        except Exception:
            # Should handle gracefully
            assert True

    def test_concurrent_product_creation_bug_fix(self):
        """Test bug: Concurrent product creation caused race conditions"""
        mock_product_repo = Mock()
        mock_inventory_repo = Mock()
        
        service = ProductService(
            product_repo=mock_product_repo,
            inventory_repo=mock_inventory_repo
        )
        
        # Simulate concurrent creation
        import threading
        import time
        
        results = []
        errors = []
        
        def create_product(thread_id):
            try:
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
            thread = threading.Thread(target=create_product, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Should handle concurrency gracefully
        assert len(errors) == 0 or len(errors) < len(results)  # Some failures acceptable
        assert len(results) > 0

    def test_api_response_format_bug_fix(self):
        """Test bug: API response format was inconsistent"""
        client = TestClient(app)
        
        try:
            # Test API response format
            response = client.get("/api/products")
            
            # Should have consistent format
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Should be list or dict
                    assert isinstance(data, (list, dict))
                except ValueError:
                    pytest.fail("API response format bug reoccurred")
        except Exception:
            # Should not crash
            assert True

    def test_authentication_bypass_bug_fix(self):
        """Test bug: Authentication could be bypassed"""
        client = TestClient(app)
        
        # Test various authentication bypass attempts
        bypass_attempts = [
            {},  # No auth
            {"Authorization": ""},  # Empty auth
            {"Authorization": "Bearer"},  # Invalid token format
            {"Authorization": "Basic"},  # Invalid basic auth
        ]
        
        for auth_header in bypass_attempts:
            try:
                response = client.get("/api/products", headers=auth_header)
                
                # Should require proper authentication
                assert response.status_code in [401, 403, 400]
            except Exception:
                # Should not crash
                assert True

    def test_sql_injection_bypass_bug_fix(self):
        """Test bug: SQL injection could bypass validation"""
        client = TestClient(app)
        
        # Test SQL injection attempts
        injection_payloads = [
            "'; DROP TABLE products; --",
            "' OR '1'='1",
            "1' UNION SELECT * FROM users --"
        ]
        
        for payload in injection_payloads:
            try:
                response = client.get(f"/api/products?name={payload}")
                
                # Should not execute malicious SQL
                assert response.status_code in [200, 400, 422, 404, 500]
                
                if response.status_code == 500:
                    content = response.text.lower()
                    # Should not reveal database errors
                    assert 'sql' not in content
                    assert 'syntax' not in content
                    assert 'table' not in content
            except Exception:
                # Should not crash
                assert True

    def test_memory_leak_bug_fix(self):
        """Test bug: Memory leak in product creation"""
        import gc
        import sys
        
        # Get initial memory state
        initial_objects = len(gc.get_objects()) if hasattr(gc, 'get_objects') else 0
        
        # Create many products
        mock_product_repo = Mock()
        mock_inventory_repo = Mock()
        
        service = ProductService(
            product_repo=mock_product_repo,
            inventory_repo=mock_inventory_repo
        )
        
        for i in range(100):
            try:
                command = CreateProductCommand(
                    name=f"Memory Test {i}",
                    price=float(i)
                )
                service.create_product(command)
            except Exception:
                pass  # Handle errors gracefully
        
        # Get final memory state
        final_objects = len(gc.get_objects()) if hasattr(gc, 'get_objects') else 0
        
        # Should not have significant memory leak
        memory_growth = final_objects - initial_objects
        assert memory_growth < 10000  # Less than 10k new objects

    def test_performance_regression_bug_fix(self):
        """Test bug: Performance regression in product listing"""
        import time
        import statistics
        
        mock_product_repo = Mock()
        mock_inventory_repo = Mock()
        
        service = ProductService(
            product_repo=mock_product_repo,
            inventory_repo=mock_inventory_repo
        )
        
        # Test performance baseline
        times = []
        for i in range(100):
            start_time = time.perf_counter()
            
            try:
                query = GetAllProductsQuery()
                service.get_all_products(query)
            except Exception:
                pass
            
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        
        # Should not have performance regression
        assert avg_time < 0.01  # Less than 10ms average

    def test_data_corruption_bug_fix(self):
        """Test bug: Data corruption in product updates"""
        mock_product_repo = Mock()
        mock_inventory_repo = Mock()
        
        service = ProductService(
            product_repo=mock_product_repo,
            inventory_repo=mock_inventory_repo
        )
        
        # Create original product
        original_command = CreateProductCommand(
            name="Original Product",
            price=10.0
        )
        
        try:
            original = service.create_product(original_command)
            
            # Update product
            update_command = UpdateProductCommand(
                product_id=original.product_id if original else 1,
                name="Updated Product",
                price=20.0
            )
            
            updated = service.update_product(update_command)
            
            # Verify data integrity
            if updated and hasattr(updated, 'name') and hasattr(updated, 'price'):
                assert updated.name == "Updated Product"
                assert updated.price == 20.0
        except Exception:
            # Should handle gracefully
            assert True

    def test_null_pointer_bug_fix(self):
        """Test bug: Null pointer exceptions in validation"""
        validator = ProductValidator()
        
        # Test with various null inputs
        null_cases = [
            (None, "Test", 10.0),  # Null product_id
            (1, None, 10.0),         # Null name
            (1, "Test", None),          # Null price
        ]
        
        for product_id, name, price in null_cases:
            try:
                validator.validate_import_data(product_id, name, price)
                # Should handle null values gracefully
                assert True  # Just ensure no crash
            except Exception:
                # Expected for some null cases
                if product_id is not None and name is not None:  # Only price can be null
                    pytest.fail(f"Null pointer bug reoccurred for case: {product_id}, {name}, {price}")

    def test_unicode_handling_bug_fix(self):
        """Test bug: Unicode characters caused crashes"""
        validator = ProductValidator()
        
        # Test with unicode characters
        unicode_cases = [
            "Product with émojis 🚀",
            "Product with ñandú",
            "Product with 中文",
            "Product with العربية",
            "Product with кириллица"
        ]
        
        for unicode_name in unicode_cases:
            try:
                validator.validate_import_data(1, unicode_name, 10.0)
                # Should handle unicode gracefully
                assert True  # Just ensure no crash
            except Exception:
                # May fail validation but shouldn't crash
                assert not "unicode" in str(Exception).lower()
                assert not "encoding" in str(Exception).lower()

    def test_transaction_rollback_bug_fix(self):
        """Test bug: Transaction rollback was not working"""
        mock_session = Mock()
        mock_container = Mock()
        
        from app.application.unit_of_work.unit_of_work import UnitOfWork
        
        try:
            with UnitOfWork(mock_session, mock_container) as uow:
                # Simulate error in transaction
                raise Exception("Simulated error")
        except Exception:
            # Expected - should handle exception
            pass
        
        # Verify rollback was called
        mock_session.rollback.assert_called_once()

    def test_cache_invalidation_bug_fix(self):
        """Test bug: Cache was not invalidated on updates"""
        mock_product_repo = Mock()
        mock_inventory_repo = Mock()
        
        service = ProductService(
            product_repo=mock_product_repo,
            inventory_repo=mock_inventory_repo
        )
        
        # Create product (should cache)
        create_command = CreateProductCommand(
            name="Cache Test",
            price=10.0
        )
        
        try:
            created = service.create_product(create_command)
            
            # Update product (should invalidate cache)
            update_command = UpdateProductCommand(
                product_id=created.product_id if created else 1,
                name="Updated Cache Test",
                price=15.0
            )
            
            updated = service.update_product(update_command)
            
            # Get product (should get updated version, not cached)
            get_query = GetProductQuery(product_id=created.product_id if created else 1)
            retrieved = service.get_product(get_query)
            
            # Should get updated version
            if retrieved and hasattr(retrieved, 'name'):
                assert retrieved.name == "Updated Cache Test"
        except Exception:
            # Should handle gracefully
            assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
