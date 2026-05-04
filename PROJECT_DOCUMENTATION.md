# WMS Project Documentation

## Overview

The Warehouse Management System (WMS) is a comprehensive, modern web application built with Python FastAPI, following Clean Architecture principles. It provides complete warehouse operations management with role-based access control, real-time inventory tracking, and advanced AI capabilities.

## Technology Stack

### Backend Framework
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.12+** - Primary programming language
- **SQLAlchemy 2.0+** - ORM for database operations
- **Alembic** - Database migration tool
- **Pydantic** - Data validation and settings management

### Database & Storage
- **PostgreSQL 16** - Primary relational database
- **ChromaDB** - Vector database for AI operations
- **FAISS** - Vector similarity search

### AI & Machine Learning
- **LangChain** - LLM orchestration framework
- **LangGraph** - Workflow orchestration for complex AI pipelines
- **Sentence Transformers** - Text embeddings
- **Groq** - LLM provider (Llama models)
- **HuggingFace** - Model hub and embeddings

### Authentication & Security
- **JWT** - JSON Web Tokens for authentication
- **bcrypt** - Password hashing
- **Passlib** - Password management library

### Development & Deployment
- **Docker & Docker Compose** - Containerization
- **Uvicorn** - ASGI server
- **Gunicorn** - Production WSGI server
- **pytest** - Testing framework
- **Black** - Code formatting
- **MyPy** - Static type checking

## Architecture

### Clean Architecture Implementation

The project follows Clean Architecture principles with clear separation of concerns:

```
src/
├── app/                          # Main application
│   ├── api/                      # API layer (FastAPI endpoints)
│   ├── modules/                  # Business modules (DDD)
│   │   ├── users/               # User management
│   │   ├── warehouses/          # Warehouse operations
│   │   ├── products/            # Product catalog
│   │   ├── inventory/           # Inventory tracking
│   │   ├── documents/           # Document management
│   │   ├── customers/           # Customer management
│   │   ├── audit/               # Audit logging
│   │   └── positions/           # Position management
│   ├── shared/                  # Shared components
│   │   ├── core/               # Core functionality
│   │   ├── domain/             # Domain entities
│   │   ├── application/        # Application services
│   │   └── utils/              # Utilities
│   └── main.py                  # Application entry point
└── ai_engine/                   # AI capabilities
    ├── core/                   # AI engine orchestration
    ├── retrieval/              # Document retrieval
    ├── generation/             # Response generation
    ├── agents/                 # WMS-specific agents
    ├── workflows/              # AI workflows
    └── config/                 # AI configuration
```

### Domain-Driven Design (DDD)

Each business module follows DDD patterns:

```
modules/{domain}/
├── domain/
│   ├── entities/              # Domain entities
│   ├── interfaces/           # Repository interfaces
│   └── exceptions/           # Domain exceptions
├── application/
│   ├── services/             # Application services
│   ├── dtos/                 # Data transfer objects
│   └── commands/             # Command/Query objects
├── infrastructure/
│   ├── repositories/         # Repository implementations
│   └── models/               # Database models
└── api/
    └── endpoints/            # API endpoints
```

## Core Features

### 1. User Management & Authentication
- **Role-Based Access Control (RBAC)**: Admin, Warehouse, Sales, Accountant roles
- **JWT Authentication**: Secure token-based authentication
- **Password Security**: bcrypt hashing with salt
- **User Profiles**: Full name, email, role management

### 2. Warehouse Operations
- **Multi-Warehouse Support**: Manage multiple warehouse locations
- **Warehouse Operations**: Transfer, receive, ship operations
- **Location Management**: Bin and position tracking
- **Capacity Management**: Warehouse capacity tracking

### 3. Inventory Management
- **Real-time Tracking**: Live inventory levels across warehouses
- **Product Catalog**: Comprehensive product information
- **Stock Movements**: Complete audit trail of inventory changes
- **Low Stock Alerts**: Automated notifications for low inventory

### 4. Document Management
- **Import Documents**: Purchase orders and receiving
- **Export Documents**: Shipping and delivery
- **Transfer Documents**: Inter-warehouse transfers
- **Document Workflow**: Approval and status tracking

### 5. Customer Management
- **Customer Profiles**: Company information and contacts
- **Order History**: Complete order tracking
- **Credit Management**: Customer credit limits and terms

### 6. Reporting & Analytics
- **Inventory Reports**: Stock levels, movements, valuations
- **Sales Reports**: Revenue, orders, customer analytics
- **Warehouse Reports**: Efficiency, capacity, operations
- **Audit Reports**: Complete audit trail

### 7. AI Engine (Advanced Features)
- **Hybrid RAG**: Combines semantic search with keyword search
- **Intelligent Agents**: Database-integrated AI agents
- **Quality Evaluation**: Automated response quality assessment
- **Multi-Mode Processing**: RAG, Agent, and Hybrid modes

## API Design

### RESTful API Structure

The API follows RESTful conventions with versioned endpoints:

```
/api/v1/
├── auth/                     # Authentication endpoints
│   ├── login               # User login
│   ├── refresh             # Token refresh
│   └── logout              # User logout
├── users/                   # User management
├── warehouses/              # Warehouse operations
├── products/               # Product catalog
├── inventory/              # Inventory management
├── documents/              # Document management
├── customers/              # Customer management
├── reports/                # Reporting endpoints
├── audit-events/           # Audit logging
└── positions/              # Position management
```

### Authentication Flow

1. **Login**: POST `/api/v1/auth/login`
2. **Token**: JWT access token + refresh token
3. **Authorization**: Bearer token in Authorization header
4. **Refresh**: POST `/api/v1/auth/refresh`
5. **Logout**: POST `/api/v1/auth/logout`

### Response Format

Standardized JSON response format:

```json
{
  "data": {},
  "message": "Success message",
  "status": "success|error",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Database Design

### PostgreSQL Schema

The database uses PostgreSQL with the following main tables:

- **users**: User accounts and authentication
- **warehouses**: Warehouse locations and information
- **products**: Product catalog and specifications
- **inventory**: Inventory levels by warehouse
- **customers**: Customer information
- **documents**: Transaction documents (imports/exports/transfers)
- **document_items**: Line items for documents
- **audit_events**: Audit trail for all operations

### Database Migrations

Uses Alembic for database migrations:

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## AI Engine Architecture

### Processing Modes

1. **RAG Mode**: Retrieval-Augmented Generation for knowledge queries
2. **Agent Mode**: Database-integrated agents for operational queries
3. **Hybrid Mode**: Intelligent switching between RAG and Agent

### AI Components

#### Retrieval System
- **Hybrid Search**: Combines vector embeddings with BM25 keyword search
- **Document Processing**: Automatic text chunking and preprocessing
- **Vector Storage**: ChromaDB for semantic search
- **Quality Control**: Configurable retrieval parameters

#### Generation System
- **LLM Integration**: Groq API with Llama models
- **Quality Evaluation**: Automated response quality assessment
- **Fallback Mechanisms**: Multiple generation strategies
- **Context Management**: Conversation history and context

#### Agent System
- **Database Tools**: Real-time database query capabilities
- **WMS-Specific Logic**: Understanding of warehouse operations
- **Tool Integration**: SQL query generation and execution
- **Error Handling**: Graceful failure and fallback

## Configuration Management

### Environment Variables

The application uses Pydantic Settings for configuration:

```python
# Database
DATABASE_URL=postgresql://user:pass@localhost:5433/db
DB_POOL_SIZE=50
DB_MAX_OVERFLOW=30

# API
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
RATE_LIMIT_PER_MINUTE=300

# CORS
CORS_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=true

# AI Engine
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
GROQ_API_KEY=your-api-key
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_DB_PATH=./wms_chroma_db
```

### Configuration Files

- **pyproject.toml**: Project dependencies and build configuration
- **docker-compose.yml**: Service orchestration
- **Dockerfile**: Container build instructions
- **alembic.ini**: Database migration configuration
- **pytest.ini**: Testing configuration

## Development Workflow

### Local Development

```bash
# Install dependencies
uv sync

# Start database
docker compose up -d db

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload

# Run tests
pytest
```

### Docker Development

```bash
# Full stack development
./start.sh dev

# Production mode
./start.sh prod

# With development tools
docker compose --profile dev up -d
```

### Testing Strategy

- **Unit Tests**: pytest with coverage
- **Integration Tests**: API endpoint testing
- **Database Tests**: Repository and model testing
- **AI Engine Tests**: Component and integration testing

## Security Implementation

### Authentication Security
- **JWT Tokens**: Short-lived access tokens with refresh tokens
- **Password Hashing**: bcrypt with salt
- **Rate Limiting**: Configurable per-endpoint rate limits
- **CORS Protection**: Configurable cross-origin policies

### Data Security
- **Input Validation**: Pydantic models for all inputs
- **SQL Injection Prevention**: SQLAlchemy parameterized queries
- **Audit Logging**: Complete audit trail for all operations
- **Role-Based Access**: Granular permissions by role

### Infrastructure Security
- **Environment Variables**: Sensitive data in environment
- **Docker Security**: Minimal base images and non-root users
- **Database Security**: Separate database credentials
- **API Security**: Request validation and error handling

## Performance Optimization

### Database Optimization
- **Connection Pooling**: SQLAlchemy connection pooling
- **Query Optimization**: Efficient query patterns
- **Indexing Strategy**: Proper database indexes
- **Caching**: Application-level caching where appropriate

### API Performance
- **Async Operations**: FastAPI async endpoints
- **Response Compression**: Gzip compression
- **Rate Limiting**: Prevent abuse and ensure stability
- **Health Checks**: Monitoring and alerting

### AI Engine Performance
- **Vector Indexing**: Efficient vector storage and retrieval
- **Model Caching**: LLM response caching
- **Batch Processing**: Efficient batch operations
- **Resource Management**: Memory and compute optimization

## Deployment Architecture

### Production Deployment

```yaml
# docker-compose.yml services
services:
  api:          # FastAPI application
  db:           # PostgreSQL database
  dashboard:    # Static web interface
  dev-tools:    # Adminer for database management
  tunnel:       # Cloudflare tunnel for external access
```

### Scaling Considerations
- **Horizontal Scaling**: Multiple API instances
- **Database Scaling**: Read replicas and connection pooling
- **Load Balancing**: nginx or cloud load balancer
- **Monitoring**: Health checks and metrics

## Monitoring & Observability

### Logging
- **Structured Logging**: JSON format with request IDs
- **Log Levels**: Configurable logging levels
- **Audit Logging**: Complete business operation audit trail
- **Error Tracking**: Comprehensive error logging

### Health Checks
- **API Health**: `/health` endpoint with database status
- **Database Health**: Connection and query health
- **Service Health**: Docker container health checks

### Metrics
- **Application Metrics**: Request counts, response times
- **Database Metrics**: Connection pool, query performance
- **Business Metrics**: User activity, operation counts

## Future Enhancements

### Planned Features
- **Real-time Notifications**: WebSocket-based notifications
- **Advanced Analytics**: Machine learning insights
- **Mobile Application**: React Native mobile app
- **Integration APIs**: Third-party system integrations

### Technical Improvements
- **Microservices Architecture**: Service decomposition
- **Event Sourcing**: Event-driven architecture
- **CQRS Pattern**: Command Query Responsibility Segregation
- **GraphQL API**: Alternative API interface

## Conclusion

The WMS project represents a modern, well-architected warehouse management system that combines:

- **Clean Architecture**: Maintainable and testable codebase
- **Modern Technologies**: FastAPI, PostgreSQL, Docker
- **AI Integration**: Advanced AI capabilities for warehouse operations
- **Security First**: Comprehensive security implementation
- **Scalability**: Designed for growth and performance
- **Developer Experience**: Excellent development tooling and documentation

This architecture provides a solid foundation for warehouse operations while maintaining flexibility for future enhancements and scaling requirements.
