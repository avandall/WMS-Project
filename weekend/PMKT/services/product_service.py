from ..domain.product_domain import Product
from ..repo.product_repo import ProductRepo

class ProductService:
    def __init__(self, repo: ProductRepo):
        self.repo = repo

    def create_product(self, product_id: int, name: str, price: float, description: str = None) -> Product:
        return self.repo.create_product(product_id, name, price, description)

    def get_product_details(self, product_id: int) -> Product:
        return self.repo.get_product_details(product_id)

    def update(self, product_id: int, name: str = None, price: float = None, description: str = None) -> Product:
        return self.repo.update_product(product_id, name, price, description)

    def delete_product(self, product_id: int) -> None:
        self.repo.delete(product_id)
        