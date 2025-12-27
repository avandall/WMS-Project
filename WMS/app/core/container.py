"""
Dependency Injection Container for PMKT Warehouse Management System.

This module implements a dependency injection container following Clean Architecture principles.
It centralizes the registration and resolution of all application dependencies.
"""

from typing import Dict, Type, TypeVar, Optional, Any
from abc import ABC, abstractmethod

T = TypeVar('T')

class IContainer(ABC):
    """Interface for dependency injection container."""

    @abstractmethod
    def register(self, interface: Type[T], implementation: Type[T], lifetime: str = 'singleton') -> None:
        """Register a dependency with the container."""
        pass

    @abstractmethod
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """Register a pre-created instance with the container."""
        pass

    @abstractmethod
    def resolve(self, interface: Type[T]) -> T:
        """Resolve a dependency from the container."""
        pass

    @abstractmethod
    def has_registration(self, interface: Type[T]) -> bool:
        """Check if an interface is registered."""
        pass

class Container(IContainer):
    """Concrete implementation of dependency injection container."""

    def __init__(self):
        self._registrations: Dict[Type[T], Dict[str, Any]] = {}
        self._instances: Dict[Type[T], T] = {}

    def register(self, interface: Type[T], implementation: Type[T], lifetime: str = 'singleton') -> None:
        """Register a dependency with the container.

        Args:
            interface: The interface/abstract class to register
            implementation: The concrete implementation class
            lifetime: 'singleton' or 'transient'
        """
        if lifetime not in ['singleton', 'transient']:
            raise ValueError("Lifetime must be 'singleton' or 'transient'")

        self._registrations[interface] = {
            'implementation': implementation,
            'lifetime': lifetime
        }

    def register_instance(self, interface: Type[T], instance: T) -> None:
        """Register a pre-created instance with the container."""
        self._instances[interface] = instance

    def resolve(self, interface: Type[T]) -> T:
        """Resolve a dependency from the container."""
        # Check if we have a pre-registered instance
        if interface in self._instances:
            return self._instances[interface]

        # Check if we have a registration
        if interface not in self._registrations:
            raise ValueError(f"No registration found for {interface}")

        registration = self._registrations[interface]

        if registration['lifetime'] == 'singleton':
            if interface not in self._instances:
                self._instances[interface] = self._create_instance(registration['implementation'])
            return self._instances[interface]
        else:
            # Transient - always create new instance
            return self._create_instance(registration['implementation'])

    def has_registration(self, interface: Type[T]) -> bool:
        """Check if an interface is registered."""
        return interface in self._registrations or interface in self._instances

    def _create_instance(self, implementation: Type[T]) -> T:
        """Create an instance of the implementation, resolving its dependencies."""
        # Get the constructor parameters
        init_signature = implementation.__init__.__annotations__

        # Remove 'self' and 'return' from annotations
        dependencies = {
            param: annotation
            for param, annotation in init_signature.items()
            if param not in ['self', 'return']
        }

        # Resolve dependencies
        resolved_deps = {}
        for param_name, param_type in dependencies.items():
            if self.has_registration(param_type):
                resolved_deps[param_name] = self.resolve(param_type)
            else:
                # Try to create with default parameters or None
                try:
                    resolved_deps[param_name] = param_type()
                except TypeError:
                    resolved_deps[param_name] = None

        return implementation(**resolved_deps)

# Global container instance
_container: Optional[Container] = None

def get_container() -> Container:
    """Get the global container instance."""
    global _container
    if _container is None:
        _container = Container()
        _setup_container(_container)
    return _container

def _setup_container(container: Container) -> None:
    """Setup all dependencies in the container."""
    # Import here to avoid circular imports
    from app.repositories.interfaces.interfaces import (
        IProductRepo, IInventoryRepo, IWarehouseRepo, IDocumentRepo
    )
    from app.repositories.sql.product_repo import ProductRepo
    from app.repositories.sql.inventory_repo import InventoryRepo
    from app.repositories.sql.warehouse_repo import WarehouseRepo
    from app.repositories.sql.document_repo import DocumentRepo
    from app.services.product_service import ProductService
    from app.services.inventory_service import InventoryService
    from app.services.warehouse_service import WarehouseService
    from app.services.document_service import DocumentService
    from app.services.report_service import ReportService
    from app.services.warehouse_operations_service import WarehouseOperationsService

    # Register repositories
    container.register(IProductRepo, ProductRepo, 'singleton')
    container.register(IInventoryRepo, InventoryRepo, 'singleton')
    container.register(IWarehouseRepo, WarehouseRepo, 'singleton')
    container.register(IDocumentRepo, DocumentRepo, 'singleton')

    # Register services
    container.register(ProductService, ProductService, 'singleton')
    container.register(InventoryService, InventoryService, 'singleton')
    container.register(WarehouseService, WarehouseService, 'singleton')
    container.register(DocumentService, DocumentService, 'singleton')
    container.register(ReportService, ReportService, 'singleton')
    container.register(WarehouseOperationsService, WarehouseOperationsService, 'singleton')

def resolve(interface: Type[T]) -> T:
    """Convenience function to resolve dependencies from the global container."""
    return get_container().resolve(interface)