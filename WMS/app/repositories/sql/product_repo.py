from typing import Optional
from app.models.product_domain import Product
from ..interfaces.interfaces import IProductRepo


# Repository for managing products
class ProductRepo(IProductRepo):
    def __init__(self):
        self.products = {}

    def save(self, product: Product) -> None:
        self.products[product.product_id] = product

    def get(self, product_id: int) -> Optional[Product]:
        return self.products.get(product_id)

    def get_all(self) -> list[Product]:
        return list(self.products.values())

    def get_price(self, product_id: int) -> float:
        product = self.products.get(product_id)
        if product:
            return product.price
        raise KeyError("Product not found")

    def delete(self, product_id: int) -> None:
        if product_id in self.products:
            del self.products[product_id]
        else:
            raise KeyError("Product not found")

    def get_product_details(self, product_id: int) -> Product:
        product = self.get(product_id)
        if not product:
            raise KeyError("Product not found")
        return product
