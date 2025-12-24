# PMKT Warehouse Management System

A comprehensive Warehouse Management System (WMS) built with Python, implementing Clean Architecture and Domain-Driven Design principles.

## 🚀 Features

- **Product Management**: Create, update, and track products with validation
- **Inventory Control**: Real-time inventory tracking across multiple warehouses
- **Warehouse Operations**: Add/remove products from warehouses with stock validation
- **Document Processing**: Handle import, export, and transfer documents
- **Reporting**: Generate comprehensive inventory and product reports
- **REST API**: Full REST API built with FastAPI
- **Clean Architecture**: Well-structured codebase following SOLID principles

## 🏗️ Architecture

This project implements **Clean Architecture** with clear separation of concerns:

### **Layer Structure**
```
PMKT/
├── api/                # REST API layer (FastAPI)
│   ├── __init__.py         # FastAPI app
│   ├── dependencies.py     # Dependency injection
│   ├── models.py          # Pydantic request/response models
│   └── routers/           # API route handlers
├── domain/             # Business entities and rules
├── repo/               # Data access layer
├── services/           # Business logic orchestration
├── module/             # Shared utilities
├── utils/              # Utilities
└── examples/           # Usage examples
```

## 📋 Requirements

- Python 3.8+
- FastAPI
- Uvicorn

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd weekend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the API server**
   ```bash
   python -m PMKT.main
   ```

   The API will be available at `http://localhost:8000`

## 🌐 API Usage

### **API Documentation**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### **Core Endpoints**

#### Products
```bash
# Create product
POST /api/v1/products/
{
  "product_id": 1,
  "name": "Laptop",
  "price": 999.99,
  "description": "High-performance laptop"
}

# Get product
GET /api/v1/products/1

# Update product
PUT /api/v1/products/1
{
  "name": "Gaming Laptop",
  "price": 1199.99
}

# Delete product
DELETE /api/v1/products/1
```

#### Warehouses
```bash
# Create warehouse
POST /api/v1/warehouses/
{
  "location": "Main Warehouse"
}

# Add product to warehouse
POST /api/v1/warehouses/1/products
{
  "product_id": 1,
  "quantity": 10
}

# Remove product from warehouse
DELETE /api/v1/warehouses/1/products
{
  "product_id": 1,
  "quantity": 5
}
```

#### Documents
```bash
# Create import document
POST /api/v1/documents/import
{
  "warehouse_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": 10,
      "unit_price": 999.99
    }
  ],
  "created_by": "John Doe"
}

# Post document (execute operations)
POST /api/v1/documents/1/post
{
  "approved_by": "Jane Smith"
}
```

#### Reports
```bash
# Get inventory report
GET /api/v1/reports/inventory

# Get warehouse-specific report
GET /api/v1/reports/inventory?warehouse_id=1
```

## 💡 Programmatic Usage

```python
from PMKT.repo.product_repo import ProductRepo
from PMKT.services.product_service import ProductService

# Initialize components
repo = ProductRepo()
service = ProductService(repo)

# Create product
product = service.create_product(1, "Laptop", 999.99)
print(f"Created: {product}")
```

## 🧪 Testing the API

```bash
# Health check
curl http://localhost:8000/health

# Create a product
curl -X POST "http://localhost:8000/api/v1/products/" \
     -H "Content-Type: application/json" \
     -d '{
       "product_id": 1,
       "name": "Test Product",
       "price": 29.99
     }'

# Get the product
curl http://localhost:8000/api/v1/products/1
```

## 🤝 Contributing

1. Follow the existing Clean Architecture patterns
2. Add API endpoints for new features
3. Include comprehensive error handling
4. Update API documentation
5. Write tests for new functionality

## 📝 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

Built as a learning project demonstrating:
- Clean Architecture principles
- Domain-Driven Design
- REST API development with FastAPI
- Python best practices
