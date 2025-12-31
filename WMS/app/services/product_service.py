from typing import Optional
from app.models.product_domain import Product
from app.repositories.interfaces.interfaces import IProductRepo, IInventoryRepo
from app.exceptions.business_exceptions import (
    ValidationError,
    EntityAlreadyExistsError,
    EntityNotFoundError,
)


class ProductService:
    """
    Service layer for product management orchestration.
    Handles business logic coordination between repositories and domain validation.
    """

    def __init__(self, product_repo: IProductRepo, inventory_repo: IInventoryRepo):
        self.product_repo = product_repo
        self.inventory_repo = inventory_repo

    def create_product(
        self,
        product_id: int,
        name: str,
        price: float,
        description: Optional[str] = None,
    ) -> Product:
        """
        Create a new product with business orchestration.
        - Validates business rules (product doesn't already exist)
        - Creates the product domain entity
        - Initializes inventory for the product
        """
        # Business rule: Check if product already exists
        existing_product = self.product_repo.get(product_id)
        if existing_product:
            raise EntityAlreadyExistsError(
                f"Product with ID {product_id} already exists"
            )

        # Create product domain entity (validation happens in constructor)
        product = Product(
            product_id=product_id, name=name, price=price, description=description
        )

        # Persist the product
        self.product_repo.save(product)

        # Initialize inventory for the new product
        self.inventory_repo.add_quantity(product_id, 0)

        return product

    def get_product_details(self, product_id: int) -> Product:
        """
        Get product details with business validation.
        """
        product = self.product_repo.get(product_id)
        if not product:
            raise EntityNotFoundError(f"Product with ID {product_id} not found")
        return product

    def update_product(
        self,
        product_id: int,
        name: Optional[str] = None,
        price: Optional[float] = None,
        description: Optional[str] = None,
    ) -> Product:
        """
        Update product with business orchestration.
        - Validates that product exists
        - Applies updates through domain entity for validation
        - Handles business rules for updates
        """
        # Get existing product
        product = self.get_product_details(product_id)

        # Apply updates through domain entity (validation happens here)
        if name is not None:
            product.update_name(name)
        if price is not None:
            product.update_price(price)
        if description is not None:
            product.update_description(description)

        # Persist changes
        self.product_repo.save(product)

        return product

    def delete_product(self, product_id: int) -> None:
        """
        Delete product with business orchestration.
        - Validates that product exists
        - Checks business rules (e.g., can't delete if in use)
        - Cleans up related data (inventory)
        """
        # Validate product exists
        self.get_product_details(product_id)

        # Business rule: Check if product has inventory (could prevent deletion)
        current_quantity = self.inventory_repo.get_quantity(product_id)
        if current_quantity > 0:
            raise ValidationError(
                f"Cannot delete product {product_id}: still has {current_quantity} items in inventory"
            )

        # Clean up inventory
        # Note: In a real system, you might want to keep historical data
        self.inventory_repo.remove_quantity(product_id, current_quantity)

        # Delete the product
        self.product_repo.delete(product_id)

    def get_product_with_inventory(self, product_id: int) -> dict:
        """
        Get product with current inventory information.
        Orchestrates between product and inventory repositories.
        """
        product = self.get_product_details(product_id)
        quantity = self.inventory_repo.get_quantity(product_id)

        return {"product": product, "current_inventory": quantity}

    def list_products_with_inventory(self) -> list:
        """
        List all products with their current inventory levels.
        """
        products = []
        for product_id, product in self.product_repo.get_all().items():
            quantity = self.inventory_repo.get_quantity(product_id)
            products.append({"product": product, "current_inventory": quantity})
        return products
