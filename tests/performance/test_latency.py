"""
Performance Tests - Test latency and response times
Tests API and service performance under various loads
"""

import pytest
import time
import asyncio
import statistics
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock

from app.application.services.product_service import ProductService
from app.application.commands.product_commands import CreateProductCommand


class TestLatencyPerformance:
    """Test latency and response time performance"""

    def test_command_creation_latency(self):
        """Test command creation latency"""
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
        p95_time = statistics.quantiles(times, n=100)[94]  # 95th percentile
        
        # Performance assertions
        assert avg_time < 0.001  # Average < 1ms
        assert p95_time < 0.002   # 95th percentile < 2ms
        assert max(times) < 0.01   # Max < 10ms

    def test_service_creation_latency(self):
        """Test service creation latency"""
        iterations = 100
        times = []
        
        for i in range(iterations):
            start_time = time.perf_counter()
            
            mock_product_repo = Mock()
            mock_inventory_repo = Mock()
            service = ProductService(
                product_repo=mock_product_repo,
                inventory_repo=mock_inventory_repo
            )
            
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        p95_time = statistics.quantiles(times, n=100)[94]
        
        # Performance assertions
        assert avg_time < 0.005   # Average < 5ms
        assert p95_time < 0.01    # 95th percentile < 10ms

    def test_concurrent_command_creation(self):
        """Test concurrent command creation performance"""
        iterations = 100
        num_threads = 4
        
        def create_commands(thread_id):
            times = []
            for i in range(iterations // num_threads):
                start_time = time.perf_counter()
                command = CreateProductCommand(
                    name=f"Thread {thread_id} Command {i}",
                    price=float(i)
                )
                end_time = time.perf_counter()
                times.append(end_time - start_time)
            return times
        
        # Run in parallel
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(create_commands, i) for i in range(num_threads)]
            all_times = []
            for future in futures:
                thread_times = future.result()
                all_times.extend(thread_times)
        
        avg_time = statistics.mean(all_times)
        p95_time = statistics.quantiles(all_times, n=100)[94]
        
        # Performance assertions
        assert avg_time < 0.002   # Average < 2ms
        assert p95_time < 0.005   # 95th percentile < 5ms

    def test_memory_allocation_performance(self):
        """Test memory allocation performance"""
        import sys
        
        # Get initial memory
        initial_objects = len(gc.get_objects()) if hasattr(gc, 'get_objects') else 0
        
        commands = []
        for i in range(1000):
            command = CreateProductCommand(
                name=f"Memory Test {i}",
                price=float(i)
            )
            commands.append(command)
        
        # Get final memory
        final_objects = len(gc.get_objects()) if hasattr(gc, 'get_objects') else 0
        
        # Memory assertions
        memory_growth = final_objects - initial_objects
        assert memory_growth < 10000  # Less than 10k new objects
        
        # Cleanup
        del commands

    def test_database_connection_latency(self):
        """Test database connection latency (mocked)"""
        mock_session = Mock()
        mock_container = Mock()
        
        times = []
        for i in range(100):
            start_time = time.perf_counter()
            
            # Simulate database operation
            with mock_session.begin():
                pass
            
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        p95_time = statistics.quantiles(times, n=100)[94]
        
        # Performance assertions
        assert avg_time < 0.01   # Average < 10ms
        assert p95_time < 0.02    # 95th percentile < 20ms

    def test_api_response_latency(self):
        """Test API response latency (mocked)"""
        from fastapi.testclient import TestClient
        from app.api import app
        
        client = TestClient(app)
        times = []
        
        for i in range(50):
            start_time = time.perf_counter()
            
            try:
                response = client.get("/api/products")
                # Record response time regardless of status
            except Exception:
                pass
            
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        p95_time = statistics.quantiles(times, n=100)[94]
        
        # Performance assertions
        assert avg_time < 0.1    # Average < 100ms
        assert p95_time < 0.2     # 95th percentile < 200ms

    def test_batch_operation_latency(self):
        """Test batch operation latency"""
        mock_product_repo = Mock()
        mock_inventory_repo = Mock()
        
        service = ProductService(
            product_repo=mock_product_repo,
            inventory_repo=mock_inventory_repo
        )
        
        batch_sizes = [10, 50, 100, 500]
        results = {}
        
        for batch_size in batch_sizes:
            start_time = time.perf_counter()
            
            for i in range(batch_size):
                try:
                    command = CreateProductCommand(
                        name=f"Batch Product {i}",
                        price=float(i)
                    )
                    service.create_product(command)
                except Exception:
                    # Handle validation errors
                    pass
            
            end_time = time.perf_counter()
            total_time = end_time - start_time
            avg_per_operation = total_time / batch_size
            
            results[batch_size] = {
                'total_time': total_time,
                'avg_time': avg_per_operation
            }
        
        # Performance assertions
        for batch_size, metrics in results.items():
            assert metrics['avg_time'] < 0.01  # Each operation < 10ms
            assert metrics['total_time'] < batch_size * 0.01  # Total time reasonable

    def test_stress_performance(self):
        """Test performance under stress"""
        iterations = 1000
        num_threads = 8
        
        def stress_test(thread_id):
            times = []
            errors = 0
            
            for i in range(iterations // num_threads):
                start_time = time.perf_counter()
                
                try:
                    command = CreateProductCommand(
                        name=f"Stress Test {thread_id}-{i}",
                        price=float(i)
                    )
                    # Simulate processing
                    time.sleep(0.001)  # 1ms processing
                except Exception:
                    errors += 1
                
                end_time = time.perf_counter()
                times.append(end_time - start_time)
            
            return {
                'times': times,
                'errors': errors,
                'thread_id': thread_id
            }
        
        # Run stress test
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(stress_test, i) for i in range(num_threads)]
            results = [future.result() for future in futures]
        
        # Analyze results
        all_times = []
        total_errors = 0
        for result in results:
            all_times.extend(result['times'])
            total_errors += result['errors']
        
        avg_time = statistics.mean(all_times)
        p95_time = statistics.quantiles(all_times, n=100)[94]
        
        # Performance assertions under stress
        assert avg_time < 0.005   # Average < 5ms under stress
        assert p95_time < 0.01    # 95th percentile < 10ms under stress
        assert total_errors < iterations * 0.1  # Less than 10% error rate

    def test_performance_regression_detection(self):
        """Test performance regression detection"""
        baseline_time = 0.001  # 1ms baseline
        
        # Test current performance
        times = []
        for i in range(100):
            start_time = time.perf_counter()
            command = CreateProductCommand(name="Regression Test", price=10.0)
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        current_avg = statistics.mean(times)
        
        # Regression detection
        regression_ratio = current_avg / baseline_time
        
        # Should not regress significantly
        assert regression_ratio < 2.0  # Less than 2x slower than baseline
        assert current_avg < 0.002  # Still under 2ms average

    def test_performance_monitoring_metrics(self):
        """Test performance monitoring and metrics collection"""
        metrics = {
            'total_operations': 0,
            'total_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'errors': 0
        }
        
        # Simulate operations with monitoring
        for i in range(100):
            start_time = time.perf_counter()
            
            try:
                command = CreateProductCommand(
                    name=f"Monitored {i}",
                    price=float(i)
                )
                
                # Simulate processing
                if i % 10 == 0:
                    raise Exception("Simulated error")
                    
            except Exception:
                metrics['errors'] += 1
                operation_time = float('inf')
            else:
                operation_time = time.perf_counter() - start_time
            
            # Update metrics
            metrics['total_operations'] += 1
            metrics['total_time'] += operation_time
            metrics['min_time'] = min(metrics['min_time'], operation_time)
            metrics['max_time'] = max(metrics['max_time'], operation_time)
        
        # Calculate derived metrics
        if metrics['total_operations'] > 0:
            metrics['avg_time'] = metrics['total_time'] / metrics['total_operations']
            metrics['success_rate'] = (metrics['total_operations'] - metrics['errors']) / metrics['total_operations']
        
        # Monitoring assertions
        assert metrics['total_operations'] == 100
        assert metrics['errors'] == 10  # 10% error rate
        assert metrics['success_rate'] == 0.9
        assert metrics['avg_time'] < 0.01  # Average < 10ms


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
