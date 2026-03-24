# PMKT Warehouse Management System

A comprehensive Warehouse Management System (WMS) built with Python, implementing Clean Architecture and Domain-Driven Design principles.

## 🚀 Features

- **Product Management**: Create, update, and track products with validation (product `price` is catalog/list; transactional pricing is per document item `unit_price`)
- **Inventory Control**: Real-time inventory tracking across multiple warehouses
- **Warehouse Operations**: Inventory moves are performed via documents (import/export/transfer) with stock validation
- **Document Processing**: Handle import, export, and transfer documents
- **Reporting**: Generate comprehensive inventory and product reports
- **REST API**: Full REST API built with FastAPI
- **Clean Architecture**: Well-structured codebase following SOLID principles

## 🏗️ Architecture

This project implements **Clean Architecture** with clear separation of concerns:

### **Layer Structure**
```
WMS/
├── src/                         # Application source tree
│   ├── app/                     # Main application package
│   │   ├── api/                 # API layer (routers/schemas/deps)
│   │   ├── core/                # Config & infrastructure
│   │   ├── models/              # Domain models
│   │   ├── repositories/        # Data access layer
│   │   ├── services/            # Business logic layer
│   │   └── utils/               # Utilities
│   ├── tests/                   # Test suite
│   ├── scripts/                 # Utility scripts
│   └── main.py                  # API entry point
├── .env                         # Environment variables
├── .env.docker                  # Docker-compose environment
├── Dockerfile                   # Container build
├── docker-compose.yml           # Local stack (API + Postgres + dashboard)
├── pyproject.toml               # Project metadata
├── uv.lock                      # Locked dependencies (uv)
├── requirements.txt             # Pip dependencies (fallback)
└── pytest.ini                   # Test configuration
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
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
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
# From the WMS directory with virtual environment activated
python src/main.py
```

Or run as a module:
```bash
source .venv/bin/activate
PYTHONPATH=src python -m app.main
```

The API will be available at: **http://localhost:8000** (or **http://0.0.0.0:8000**)

### **Troubleshooting**

**"ModuleNotFoundError: No module named 'uvicorn'"**
- Make sure you're running from the WMS directory
- Activate the virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -e .`

**"python: command not found"**
- Use `python3` instead of `python`
- Or use the convenience script: `./run_server.sh`

**Server not starting**
- Check if port 8000 is already in use: `lsof -i :8000`
- Kill existing process: `pkill -f uvicorn`
- Try different port by setting `PORT` environment variable

### **API Documentation**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🧪 Testing

### **Run All Tests**
```bash
pytest
```

### **Run Unit Tests Only**
```bash
pytest tests/unit/
```

### **Run Integration Tests**
```bash
pytest tests/integration/
```

### **Run Comprehensive End-to-End Test**
```bash
# Make sure server is running first
python main.py

# In another terminal:
python tests/comprehensive_test.py
```

See [tests/COMPREHENSIVE_TEST_README.md](tests/COMPREHENSIVE_TEST_README.md) for details.

### **Run with Coverage**
```bash
pytest --cov=app --cov-report=html
```

## 🛠️ Utility Scripts

All utility scripts are located in the `scripts/` directory. See [scripts/README.md](scripts/README.md) for full documentation.

### **Setup Admin User**
```bash
python scripts/create_admin.py
```
Creates admin user (admin@example.com / admin) with bcrypt password hashing.

### **Database Migrations**
```bash
python scripts/add_customer_id.py
```
Adds customer_id column to documents table (safe to run multiple times).

### **Database Inspection**
```bash
# View all tables and schema
python scripts/test_db.py

# Check warehouse data
python scripts/check_warehouses.py
```

## 📖 Usage Examples

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
