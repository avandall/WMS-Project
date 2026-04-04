# WMS CI/CD Pipeline Setup Guide

## 🚀 **Overview**

This guide explains the complete CI/CD pipeline setup for the WMS (Warehouse Management System) project using GitHub Actions and Docker.

## 📁 **Project Structure**

```
.github/
├── workflows/
│   └── ci.yml              # Main CI/CD pipeline
docker/
├── nginx.conf               # Production nginx configuration
├── prometheus.yml           # Monitoring configuration
├── grafana/
│   ├── dashboards/        # Pre-configured dashboards
│   └── datasources/       # Data source configurations
└── init-db.sql            # Database initialization
```

## 🔄 **CI/CD Pipeline Workflow**

### **Triggers**
- **Push to main/develop**: Runs full pipeline
- **Pull requests**: Runs tests only
- **Releases**: Triggers deployment to production

### **Jobs Overview**

#### **1. Quality Checks** ✅
```yaml
quality-checks:
  - Code formatting (Black)
  - Linting (Flake8)
  - Type checking (MyPy)
  - Security scanning (Bandit + Safety)
```

#### **2. Backend Testing** 🧪
```yaml
backend-tests:
  - Unit tests with pytest
  - Integration tests with PostgreSQL
  - SQL security tests
  - AI engine tests
  - Coverage reporting
```

#### **3. Frontend Testing** 🎨
```yaml
frontend-tests:
  - ESLint checking
  - Jest/React testing
  - Build verification
```

#### **4. AI Engine Testing** 🤖
```yaml
ai-engine-test:
  - Indexer functionality tests
  - Code search validation
  - Vector store operations
```

#### **5. Build & Security** 🏗️
```yaml
build-and-scan:
  - Python package building
  - Docker image building
  - Vulnerability scanning
  - Artifact uploading
```

#### **6. Docker Build** 🐳
```yaml
docker-build:
  - Multi-stage Docker build
  - Multi-architecture support (amd64/arm64)
  - Docker Hub pushing
```

#### **7. Deployment** 🚀
```yaml
deploy-staging:    # Deploy to develop branch
deploy-production: # Deploy to releases
```

## 🐳 **Docker Configuration**

### **Multi-Stage Dockerfile**
```dockerfile
# Base stage - Python dependencies
FROM python:3.13-slim AS base

# Frontend stage - Node.js build  
FROM node:20-alpine AS frontend-builder

# Production stage - Nginx
FROM nginx:alpine AS production
```

### **Docker Compose Services**

#### **Development Environment**
```yaml
services:
  db:           # PostgreSQL 15
  redis:         # Redis for caching
  api:           # FastAPI backend
  dashboard:      # React development server
  dev-tools:      # Adminer for database access
```

#### **Production Environment**
```yaml
services:
  nginx:          # Reverse proxy with SSL
  prometheus:     # Metrics collection
  grafana:        # Visualization dashboards
```

### **Environment Configuration**

#### **Development (.env.dev)**
```bash
ENVIRONMENT=development
DEBUG=true
AUTO_SEED_DATA=true
AI_PROVIDER=groq
AI_MODEL=llama-3.1-8b-instant
```

#### **Production (.env.prod)**
```bash
ENVIRONMENT=production
DEBUG=false
AI_MODEL=llama-3.3-70b-versatile
RATE_LIMIT_PER_MINUTE=100
```

## 🔧 **Setup Instructions**

### **1. Repository Setup**

#### **Enable GitHub Actions**
```bash
# 1. Create necessary directories
mkdir -p .github/workflows

# 2. Add workflow file (already created)
cp ci.yml .github/workflows/

# 3. Configure secrets in GitHub
# Go to Settings > Secrets and variables > Actions
# Add: DOCKER_USERNAME, DOCKER_PASSWORD, GROQ_API_KEY
```

#### **Environment Files Setup**
```bash
# Development
cp .env.docker .env.dev

# Production  
cp .env.docker .env.prod
# Add production-specific values
```

### **2. Local Development**

#### **Start Development Environment**
```bash
# Start all services
docker-compose up

# Start specific services
docker-compose up db redis api

# Start with custom environment
ENVIRONMENT=development docker-compose up

# Start monitoring stack
docker-compose --profile monitoring up
```

#### **Development Tools**
```bash
# Database admin interface
docker-compose --profile dev-tools up

# Access at http://localhost:8090
```

### **3. Production Deployment**

#### **Manual Deployment**
```bash
# Build and push Docker image
docker build -t wms-project:latest .
docker push wms-project:latest

# Deploy to production server
docker-compose --profile production up -d
```

#### **Automated Deployment**
```bash
# Triggered by:
# - Push to main branch
# - Creating new release
# - Manual workflow dispatch
```

## 📊 **Monitoring & Observability**

### **Prometheus Metrics**
- **Application metrics**: Request count, response time, error rate
- **System metrics**: CPU, memory, disk usage
- **Database metrics**: Connection pool, query performance
- **Custom metrics**: AI engine performance

### **Grafana Dashboards**
- **System Overview**: Infrastructure health
- **Application Performance**: API response times
- **Database Analytics**: Query performance
- **Business Metrics**: Warehouse operations KPIs

### **Health Checks**
```bash
# Application health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000/health

# Database health
docker-compose exec db pg_isready -U wms_user -d warehouse_db
```

## 🔒 **Security Configuration**

### **Container Security**
```dockerfile
# Non-root user
RUN useradd --create-home --shell /bin/bash wms
USER wms

# Read-only filesystem where possible
RUN chmod -R 755 /app

# Security headers in nginx
add_header X-Frame-Options "SAMEORIGIN"
add_header X-Content-Type-Options "nosniff"
add_header X-XSS-Protection "1; mode=block"
```

### **Secrets Management**
```yaml
# GitHub Secrets (encrypted)
DOCKER_USERNAME
DOCKER_PASSWORD
GROQ_API_KEY

# Environment variables (non-sensitive)
ENVIRONMENT
API_PORT
AI_MODEL
```

### **Network Security**
```yaml
networks:
  wms-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16  # Isolated network
```

## 🚀 **Performance Optimization**

### **Build Optimization**
```dockerfile
# Multi-stage builds reduce final image size
FROM node:20-alpine AS frontend-builder
FROM nginx:alpine AS production

# Layer caching
COPY package*.json ./
RUN npm ci --only=production
```

### **Runtime Optimization**
```yaml
# Resource limits
deploy-staging:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M

# Health checks for auto-restart
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### **Caching Strategy**
```yaml
# Docker layer caching
uses: actions/cache@v4
with:
  path: ~/.cache/pip
  key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}

# Nginx static file caching
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Build Failures**
```bash
# Check Docker logs
docker-compose logs api

# Check build artifacts
docker build --no-cache --progress=plain .

# Clear Docker cache
docker system prune -f
```

#### **Test Failures**
```bash
# Run specific test
pytest tests/unit/test_specific.py -v

# Check test database
docker-compose exec db psql -U wms_user -d warehouse_db -c "\dt"

# Check API connectivity
curl -X GET http://localhost:8000/health
```

#### **Deployment Issues**
```bash
# Check service status
docker-compose ps

# Check resource usage
docker stats

# Restart services
docker-compose restart api
```

### **Debug Mode**
```bash
# Enable debug logging
ENVIRONMENT=development DEBUG=true docker-compose up

# Run tests with coverage
pytest --cov=src --cov-report=html

# Interactive debugging
docker-compose exec api bash
```

## 📈 **Best Practices**

### **Code Quality**
- **Pre-commit hooks**: Black formatting, Flake8 linting
- **Type hints**: All functions annotated
- **Documentation**: Docstrings for all public functions
- **Testing**: >90% coverage requirement

### **Security**
- **Secrets management**: Never commit secrets
- **Vulnerability scanning**: Automated in CI/CD
- **Container security**: Non-root, read-only filesystem
- **Network isolation**: Custom Docker networks

### **Performance**
- **Resource monitoring**: Prometheus + Grafana
- **Log aggregation**: Structured logging
- **Caching**: Multi-layer caching strategy
- **Load testing**: Automated performance tests

### **Deployment**
- **Blue-green deployment**: Zero-downtime updates
- **Rollback capability**: Quick fallback on failure
- **Health monitoring**: Automated recovery
- **Environment parity**: Dev/staging/production consistency

## 🔄 **Continuous Improvement**

### **Monitoring Alerts**
```yaml
# Slack/Email notifications on:
# - Build failures
# - Test failures  
# - Deployment issues
# - Performance degradation
# - Security vulnerabilities
```

### **Automated Updates**
```bash
# Dependency updates
pip-audit --requirement requirements.txt

# Security patches
docker-compose pull && docker-compose up -d

# Performance optimization
# Regular monitoring and optimization based on metrics
```

## 📚 **Additional Resources**

### **Documentation**
- [API Documentation](./docs/api.md)
- [Deployment Guide](./docs/deployment.md)
- [Troubleshooting Guide](./docs/troubleshooting.md)

### **Tools & Scripts**
- [Local Development Scripts](./scripts/dev/)
- [Deployment Scripts](./scripts/deploy/)
- [Monitoring Scripts](./scripts/monitoring/)

### **External Integrations**
- [Slack Notifications](./integrations/slack.md)
- [Email Alerts](./integrations/email.md)
- [Monitoring Setup](./integrations/monitoring.md)

---

This CI/CD setup provides enterprise-grade deployment automation with comprehensive testing, security scanning, monitoring, and zero-downtime deployments for the WMS project.
