# PostgreSQL Database Configuration for WMS

## Connection String Format
```
postgresql://username:password@host:port/database_name
```

## Default Configuration
- **Host**: localhost
- **Port**: 5432
- **Database**: warehouse_db
- **Username**: postgres
- **Password**: postgres

## Setup Instructions

### 1. Install PostgreSQL
Download and install PostgreSQL from: https://www.postgresql.org/download/

### 2. Create Database
```sql
CREATE DATABASE warehouse_db;
```

Or using psql command line:
```bash
psql -U postgres
CREATE DATABASE warehouse_db;
\q
```

### 3. Configure Connection
Update the `.env` file in the project root:
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/warehouse_db
```

### 4. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
The application will automatically create all required tables on startup:
```bash
python app/main.py
```

## Database Schema
Tables will be created automatically:
- `products` - Product catalog
- `warehouses` - Warehouse locations
- `inventory` - Total inventory across all warehouses
- `warehouse_inventory` - Product quantities in each warehouse
- `documents` - Import/Export/Transfer documents
- `document_items` - Line items for each document

## Environment Variables
Create a `.env` file in the project root:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/warehouse_db
DEBUG=False
HOST=0.0.0.0
PORT=8000
```
