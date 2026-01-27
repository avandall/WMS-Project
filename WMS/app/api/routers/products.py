"""
Products API router.
Provides endpoints for product management operations.
"""

from fastapi import APIRouter, Depends
from ..dependencies import get_product_service
from ..schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import ProductService

router = APIRouter()


@router.get("/", response_model=list[ProductResponse])
async def get_all_products(service: ProductService = Depends(get_product_service)):
    """Get all products."""
    products = service.get_all_products()
    return [ProductResponse.from_domain(product) for product in products]


@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate, service: ProductService = Depends(get_product_service)
):
    """Create a new product."""
    created_product = service.create_product(
        product_id=product.product_id,
        name=product.name,
        price=product.price,
        description=product.description,
    )
    return ProductResponse.from_domain(created_product)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int, service: ProductService = Depends(get_product_service)
):
    """Get product details by ID."""
    product = service.get_product_details(product_id)
    return ProductResponse.from_domain(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    service: ProductService = Depends(get_product_service),
):
    """Update product information."""
    updated_product = service.update_product(
        product_id=product_id,
        name=product_update.name,
        price=product_update.price,
        description=product_update.description,
    )
    return ProductResponse.from_domain(updated_product)


@router.delete("/{product_id}")
async def delete_product(
    product_id: int, service: ProductService = Depends(get_product_service)
):
    """Delete a product."""
    service.delete_product(product_id)
    return {"message": f"Product {product_id} deleted successfully"}
