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
WMS/
├── app/                          # Main application package
│   ├── main.py                   # FastAPI app entry point
│   ├── api/                      # API layer
│   │   ├── __init__.py          # FastAPI app creation & router inclusion
│   │   ├── dependencies.py      # Dependency injection
│   │   ├── routers/             # API endpoints
│   │   │   ├── products.py
│   │   │   ├── warehouses.py
│   │   │   ├── inventory.py
│   │   │   ├── documents.py
│   │   │   └── reports.py
│   │   └── schemas/             # Pydantic models
│   │       └── product.py       # API request/response schemas
│   ├── services/                # Business logic layer
│   │   ├── product_service.py
│   │   ├── warehouse_service.py
│   │   ├── inventory_service.py
│   │   ├── document_service.py
│   │   ├── report_service.py
│   │   ├── *_report.py          # Report classes
│   ├── repositories/            # Data access layer
│   │   ├── interfaces/          # Repository contracts
│   │   │   └── interfaces.py
│   │   ├── sql/                 # SQL implementations (currently in-memory)
│   │   │   ├── product_repo.py
│   │   │   ├── warehouse_repo.py
│   │   │   ├── inventory_repo.py
│   │   │   └── document_repo.py
│   │   └── __init__.py
│   ├── models/                  # Domain models
│   │   ├── product_domain.py
│   │   ├── warehouse_domain.py
│   │   ├── inventory_domain.py
│   │   ├── document_domain.py
│   │   └── models.py            # DTOs and enums
│   ├── core/                    # Configuration & infrastructure
│   │   ├── database.py
│   │   └── error_constants.py
│   ├── exceptions/              # Custom exceptions
│   │   └── business_exceptions.py
│   └── utils/                   # Utilities
│       ├── infrastructure/
│       ├── domain/
│       └── application/
├── tests/                       # Test suite
│   ├── unit/
│   ├── integration/
│   └── functional/
├── .env                         # Environment variables
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Test configuration
└── README.md
```

## 📋 Requirements

- Python 3.8+
- FastAPI
- Uvicorn

## 🛠️ Installation & Setup

1. **Navigate to the project directory**
   ```bash
   cd WMS
   ```

2. **Create and activate virtual environment (recommended)**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment (optional)**
   - Copy `.env` and modify settings as needed
   - Default settings work for development

## 🚀 Running the Application

### **Development Server**
```bash
# From the WMS directory
python app/main.py
```

Or run as a module:
```bash
python -m app.main
```

The API will be available at: **http://localhost:8000**

### **API Documentation**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🧪 Testing

### **Run All Tests**
```bash
pytest
```

### **Run with Coverage**
```bash
pytest --cov=app --cov-report=html
```

### **Run Specific Test Categories**
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# API tests
pytest tests/api/
```

## � Docker

### **Prerequisites**
- Docker installed on your system
- Docker Compose (usually included with Docker Desktop)

### **Build and Run with Docker Compose**
```bash
# From the WMS directory
docker-compose up --build
```

The API will be available at: **http://localhost:8000**

### **Run in Background**
```bash
docker-compose up -d --build
```

### **Stop the Container**
```bash
docker-compose down
```

### **Build Docker Image Manually**
```bash
# Build the image
docker build -t wms-api .

# Run the container
docker run -p 8000:8000 wms-api
```

### **Development with Docker**
For development with live reload, the docker-compose.yml mounts the current directory as a volume, so changes to the code will be reflected immediately.

## �📖 Usage Examples

### **Quick Start**
1. Start the server: `python app/main.py`
2. Open http://localhost:8000/docs in your browser
3. Use the interactive Swagger UI to test endpoints

### **Basic Workflow**
```bash
# 1. Create a product
curl -X POST "http://localhost:8000/api/products/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "price": 999.99, "description": "Gaming laptop"}'

# 2. Create a warehouse
curl -X POST "http://localhost:8000/api/warehouses/" \
  -H "Content-Type: application/json" \
  -d '{"location": "Main Warehouse"}'

# 3. Add product to warehouse
curl -X POST "http://localhost:8000/api/warehouses/1/products" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 50}'

# 4. Check inventory
curl "http://localhost:8000/api/inventory/warehouse/1"
```

### **Python Client Example**
```python
import httpx

# Create a product
response = httpx.post(
    "http://localhost:8000/api/products/",
    json={"name": "Mouse", "price": 25.99}
)
product = response.json()
print(f"Created product: {product}")

# Get all products
response = httpx.get("http://localhost:8000/api/products/")
products = response.json()
print(f"All products: {products}")
```

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

## 🔧 Development

### **Project Structure**
```
WMS/
├── app/                    # Main application
│   ├── api/               # FastAPI routers and schemas
│   ├── core/              # Configuration and settings
│   ├── models/            # Domain models and DTOs
│   ├── repositories/      # Data access layer
│   ├── services/          # Business logic
│   ├── exceptions/        # Custom exceptions
│   └── utils/             # Utilities and helpers
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── api/              # API tests
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### **Adding New Features**
1. **Define domain models** in `app/models/`
2. **Create repository interface** in `app/repositories/interfaces/`
3. **Implement repository** in `app/repositories/sql/`
4. **Add business logic** in `app/services/`
5. **Create API endpoints** in `app/api/routers/`
6. **Add Pydantic schemas** in `app/api/schemas/`
7. **Write comprehensive tests**

### **Environment Configuration**
Edit `.env` file to configure:
- Database connection
- Server settings
- Debug mode
- Security settings

## 🚀 Deployment

### **Production Server**
```bash
# Using uvicorn directly
uvicorn app.api:app --host 0.0.0.0 --port 8000

# With environment variables
export DATABASE_URL="sqlite:///./prod.db"
export DEBUG=false
uvicorn app.api:app --host 0.0.0.0 --port 8000
```

### **Docker Deployment** (Future)
```dockerfile
# Dockerfile example
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
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
