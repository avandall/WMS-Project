from ..domain.product_domain import Product

# Repository for managing products
class ProductRepo:
    def __init__(self):
        self.products = {}

    def save(self, product: Product) -> None:
        self.products[product.product_id] = product

    def get(self, product_id: int) -> Product:
        return self.products.get(product_id)

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

    def create_product(self, product_id: int, name: str, price: float, description: str = None) -> Product:
        product = Product(product_id=product_id, name=name, price=price, description=description)
        self.save(product)
        return product

    def get_product_details(self, product_id: int) -> Product:
        product = self.get(product_id)
        if not product:
            raise KeyError("Product not found")
        return product

    def update_product(self, product_id: int, name: str = None, price: float = None, description: str = None) -> Product:
        product = self.get(product_id)
        if not product:
            raise KeyError("Product not found")
        if name is not None:
            product.update_name(name)
        if price is not None:
            product.update_price(price)
        if description is not None:
            product.update_description(description)
        self.save(product)
        return product
        