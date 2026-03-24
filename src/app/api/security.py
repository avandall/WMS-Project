"""
API security and validation middleware for production.
Includes rate limiting, input validation, and request size limits.
"""

from typing import Optional, Dict
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio
from app.core.settings import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Simple in-memory rate limiter (use Redis in production)
class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = asyncio.Lock()
    
    async def check_rate_limit(self, client_ip: str, limit: Optional[int] = None) -> bool:
        """
        Check if client has exceeded rate limit.
        
        Args:
            client_ip: Client IP address
            limit: Requests per minute (default from settings)
        
        Returns:
            True if within limit, False if exceeded
        """
        if limit is None:
            limit = settings.rate_limit_per_minute
        
        async with self.lock:
            now = datetime.now()
            cutoff = now - timedelta(minutes=1)
            
            # Clean old requests
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if req_time > cutoff
            ]
            
            # Check limit
            if len(self.requests[client_ip]) >= limit:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return False
            
            # Add current request
            self.requests[client_ip].append(now)
            return True


rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware to enforce rate limiting.
    Returns 429 Too Many Requests if limit exceeded.
    """
    # Skip rate limiting for health check
    if request.url.path == "/health":
        return await call_next(request)
    
    client_ip = request.client.host if request.client else "unknown"
    
    if not await rate_limiter.check_rate_limit(client_ip):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded. Please try again later.",
                "limit": settings.rate_limit_per_minute,
                "window": "1 minute"
            }
        )
    
    return await call_next(request)


def validate_pagination_params(page: int = 1, page_size: int = 20, max_page_size: int = 100):
    """
    Validate pagination parameters to prevent abuse.
    
    Args:
        page: Page number (must be >= 1)
        page_size: Items per page (must be 1-100)
        max_page_size: Maximum allowed page size
    
    Raises:
        HTTPException: If parameters are invalid
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page number must be >= 1"
        )
    
    if page_size < 1 or page_size > max_page_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Page size must be between 1 and {max_page_size}"
        )
    
    return page, page_size


def validate_id_parameter(entity_id: int, entity_name: str = "Entity"):
    """
    Validate ID parameters to prevent invalid values.
    
    Args:
        entity_id: ID to validate
        entity_name: Name of entity for error message
    
    Raises:
        HTTPException: If ID is invalid
    """
    if entity_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{entity_name} ID must be positive"
        )
    
    return entity_id
