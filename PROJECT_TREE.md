# WMS Project Tree Structure

```
WMS (Warehouse Management System)
/
|-- .env*                          # Environment configuration files
|   |-- .env                       # Main environment
|   |-- .env.dev                   # Development environment
|   |-- .env.docker                # Docker environment
|   |-- .env.example               # Environment template
|   |-- .env.prod                  # Production environment
|   |-- .env.test                  # Testing environment
|
|-- .git/                          # Git version control
|-- .github/                       # GitHub workflows
|   `-- workflows/
|       `-- python-ci.yml         # CI/CD pipeline
|
|-- .pytest_cache/                 # Pytest cache
|-- .venv/                         # Virtual environment
|-- .vscode/                       # VS Code settings
|
|-- alembic/                       # Database migrations
|   |-- README                     # Alembic documentation
|   |-- env.py                     # Alembic environment
|   |-- script.py.mako             # Migration script template
|   |-- __pycache__/               # Python cache
|   `-- versions/                  # Migration versions
|       |-- 42f8cbff95a1_add_audit_logs_columns.py
|       `-- __pycache__/
|
|-- dashboard/                     # Web dashboard
|   |-- INTEGRATION_GUIDE.md       # Dashboard integration guide
|   |-- README.md                  # Dashboard documentation
|   |-- ai_engine_integration.py   # AI engine integration
|   |-- index.html                 # Main dashboard page
|   |-- node_modules/              # Node.js dependencies
|   |-- package.json               # Node.js configuration
|   |-- package-lock.json          # Node.js lock file
|   |-- playwright.config.ts       # Playwright testing config
|   |-- rapid-switching-demo.html  # Demo page
|   |-- script.js                  # Dashboard JavaScript
|   |-- styles.css                 # Dashboard styles
|   |-- test-modal.html            # Test modal
|   |-- test_persistent_ai.html    # AI persistence test
|   |-- tests/                     # Dashboard tests
|   |   `-- e2e.spec.ts           # End-to-end tests
|   `-- wms-ai-static/            # Static AI resources
|
|-- docs/                          # Documentation (empty)
|
|-- lessons/                       # Learning modules
|   |-- lesson1.py                 # Basic introduction
|   |-- lesson2.py                 # Core concepts
|   |-- lesson3.py                 # Advanced features
|   |-- lesson3-2.py               # Alternative approach
|   |-- lesson4.py                 # Database integration
|   |-- lesson4-2.py               # Database alternative
|   |-- lesson5.py                 # API development
|   |-- lesson5-2.py               # API alternative
|   |-- lesson6.py                 # Frontend integration
|   |-- lesson7.py                 # Testing strategies
|   |-- lesson8.py                 # Deployment
|   |-- lesson8-2.py               # Deployment alternative
|   |-- lesson9.py                 # Performance
|   |-- lesson10.py                # Advanced topics
|   `-- README.md                 # Lessons overview
|
|-- scripts/                       # Utility scripts
|   |-- add_wms_sample_data.py     # Sample data generator
|   |-- run_sql_exec_tests.py      # SQL execution tests
|   `-- setup_complete_wms.sh      # Complete WMS setup
|
|-- src/                           # Source code
|   |-- ai_engine/                 # AI Engine core
|   |   |-- __init__.py
|   |   |-- README.md
|   |   |-- agents/                # AI agents
|   |   |-- config/                # Configuration
|   |   |   `-- settings.py        # AI engine settings
|   |   |-- core/                  # Core AI functionality
|   |   |-- examples/              # Usage examples
|   |   |   |-- basic_usage.py     # Basic usage examples
|   |   |   |-- complete_usage_guide.py
|   |   |   `-- quick_start.py     # Quick start guide
|   |   |-- retrieval/             # Document retrieval
|   |   |   `-- document_processor.py
|   |   `-- .env.example           # AI engine env template
|   |
|   |-- app/                       # Main application
|   |   |-- __init__.py
|   |   |-- main.py                # FastAPI application entry
|   |   |-- api/                   # API endpoints
|   |   |-- application/           # Application logic
|   |   |-- core/                  # Core application features
|   |   `-- infrastructure/        # Infrastructure layer
|   |       `-- persistence/
|   |           `-- repositories/
|   |               `-- document_repo.py
|   |
|   `-- data/                      # Data management
|       |-- __init__.py
|       |-- README.md
|       |-- logs/                  # Data logs
|       |-- seed_data/             # Seed data scripts
|       |   |-- create_login_users.py
|       |   |-- generate_dev_data.py
|       |   |-- load_basic_data.py
|       |   `-- load_inventory.py
|       `-- seed_data.txt          # Seed data documentation
|
|-- tests/                         # Test suite
|   |-- comprehensive_test.py       # Comprehensive tests
|   |-- conftest.py                 # Pytest configuration
|   |-- README.md                   # Test documentation
|   |-- .env.test                   # Test environment
|   |-- functional/                 # Functional tests
|   |   `-- test_warehouse_workflows.py
|   |-- integration/                # Integration tests
|   |   |-- api/
|   |   `-- test_integration.py
|   |-- sql/                       # SQL tests
|   |   |-- README.md
|   |   |-- conftest.py
|   |   `-- test_sql_document_repo.py
|   |   |-- test_sql_operations.py
|   |   |-- test_sql_queries.py
|   |   |-- test_sql_schema.py
|   |   `-- test_sql_statements.py
|   `-- unit/                      # Unit tests
|       |-- domain/
|       |-- repo/
|       `-- services/
|
|-- vector_db/                     # Vector database storage
|   `-- 4431cb1d-89df-4ab8-94e4-ab6417a7d06f/
|       |-- data_level0.bin        # Vector data
|       |-- header.bin             # Database header
|       |-- length.bin             # Length metadata
|       `-- link_lists.bin         # Link lists
|
|-- wms_knowledge_base/             # AI knowledge base
|   |-- load_wms_knowledge_base.py  # Knowledge base loader
|   |-- wms_business_processes.md   # Business processes documentation
|   |-- wms_faq_troubleshooting.md # FAQ and troubleshooting
|   |-- wms_overview.md             # WMS overview
|   `-- wms_technical_guide.md     # Technical guide
|
|-- .gitignore                     # Git ignore rules
|-- .python-version                # Python version specification
|-- Dockerfile                     # Docker configuration
|-- README.md                      # Main project documentation
|-- TEST_AI_GUIDE.md               # AI testing guide
|-- TEST_COMMANDS.md               # Test commands reference
|-- alembic.ini                    # Alembic configuration
|-- docker-compose.yml             # Docker Compose configuration
|-- pyproject.toml                 # Python project configuration
|-- pytest.ini                    # Pytest configuration
|-- pytest-safe                   # Safe pytest runner
|-- requirements.txt               # Python dependencies
|-- run_tests.py                   # Test runner script
|-- start.sh                       # Application startup script
|-- test.db                        # Test database
|-- uv.lock                        # UV lock file
`-- wms_schema.sql                 # Database schema
```

## Directory Descriptions

### **Core Components**

- **`src/`** - Main source code directory
  - **`ai_engine/`** - AI/ML engine for intelligent warehouse management
  - **`app/`** - Main FastAPI application
  - **`data/`** - Data management and seed data

- **`dashboard/`** - Web frontend dashboard for WMS visualization

- **`tests/`** - Comprehensive test suite (unit, integration, functional, SQL)

### **Configuration & Deployment**

- **`alembic/`** - Database migration management
- **`scripts/`** - Utility and setup scripts
- **`vector_db/`** - Vector database for AI search functionality

### **Documentation & Learning**

- **`docs/`** - Project documentation (placeholder)
- **`lessons/`** - Step-by-step learning modules
- **`wms_knowledge_base/`** - AI knowledge base documentation

### **Development Tools**

- **`.github/`** - CI/CD workflows
- **`.vscode/`** - IDE configuration
- **`tests/`** - Testing infrastructure

## Key Files

- **`start.sh`** - Main application launcher
- **`docker-compose.yml`** - Container orchestration
- **`pyproject.toml`** - Python project metadata
- **`README.md`** - Project overview and setup instructions
- **`wms_schema.sql`** - Database schema definition

## Architecture Overview

The WMS project follows a **modular architecture** with:

1. **AI Engine** - Intelligent warehouse operations
2. **FastAPI Backend** - RESTful API services
3. **Web Dashboard** - User interface
4. **PostgreSQL Database** - Data persistence
5. **Vector Database** - AI-powered search
6. **Docker Compose** - Containerized deployment

This structure supports **scalable warehouse management** with **AI-driven insights** and **modern web interfaces**.
