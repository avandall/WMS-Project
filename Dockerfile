# Multi-stage production Dockerfile for WMS (Warehouse Management System)
FROM python:3.13-slim AS base

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=off \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    git \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY pyproject.toml ./pyproject.toml
COPY README.md ./README.md
COPY uv.lock ./uv.lock
COPY src ./src/
COPY ai_engine/ ./ai_engine/
COPY tests/ ./tests/
COPY run_sql_exec_tests.py .
COPY test_relevance_filter.py .

# Install Python dependencies
RUN pip install --no-cache-dir .

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/ai_engine/stores /app/ai_engine/cache

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash wms && \
    chown -R wms:wms /app
USER wms

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Production command with proper worker configuration
CMD ["gunicorn", "src.app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--workers", "4", "--timeout", "60", "--max-requests", "1000", "--max-requests-jitter", "50"]

# Frontend build stage
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY dashboard/package*.json ./

# Install frontend dependencies
RUN npm ci --only=production

# Copy frontend source
COPY dashboard/ .

# Build frontend with optimization
RUN npm run build

# Production stage with Nginx
FROM nginx:alpine AS production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built frontend from frontend stage
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Copy optimized nginx configuration
COPY docker/nginx.conf /etc/nginx/nginx.conf

# Create non-root user
RUN addgroup -g 101 nginx && \
    adduser -S -D -H -u 101 -G nginx -s /sbin/nologin nginx

# Expose web server port
EXPOSE 80

# Health check for web server
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

# Start nginx with optimized configuration
USER nginx
CMD ["nginx", "-g", "daemon off;"]
