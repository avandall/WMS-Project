"""API security and validation helpers."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional

from fastapi import HTTPException, status

from app.shared.core.logging import get_logger
from app.shared.core.redis import redis_manager
from app.shared.core.settings import settings

logger = get_logger(__name__)


class RateLimiter:
    """Redis-based distributed rate limiter."""

    def __init__(self):
        # Fallback to in-memory if Redis is not available
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = asyncio.Lock()

    async def check_rate_limit(self, client_ip: str, limit: Optional[int] = None) -> bool:
        if limit is None:
            limit = settings.rate_limit_per_minute

        # Try Redis first
        try:
            if redis_manager.client:
                return await self._redis_rate_limit(client_ip, limit)
        except Exception as e:
            logger.warning(f"Redis rate limiting failed, falling back to in-memory: {e}")

        # Fallback to in-memory rate limiting
        return await self._memory_rate_limit(client_ip, limit)

    async def _redis_rate_limit(self, client_ip: str, limit: int) -> bool:
        """Redis-based rate limiting using sliding window."""
        key = f"rate_limit:{client_ip}"
        
        # Get current count
        current_count = await redis_manager.get(key)
        if current_count is None:
            current_count = 0
        else:
            current_count = int(current_count)
        
        if current_count >= limit:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return False
        
        # Increment counter with expiration
        new_count = await redis_manager.increment(key)
        if new_count == 1:  # First request in this window
            await redis_manager.expire(key, 60)  # 1 minute window
        
        return new_count <= limit

    async def _memory_rate_limit(self, client_ip: str, limit: int) -> bool:
        """In-memory rate limiting as fallback."""
        async with self.lock:
            now = datetime.now()
            cutoff = now - timedelta(minutes=1)
            self.requests[client_ip] = [
                t for t in self.requests[client_ip] if t > cutoff
            ]
            if len(self.requests[client_ip]) >= limit:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return False
            self.requests[client_ip].append(now)
            return True


rate_limiter = RateLimiter()


def validate_pagination_params(page: int = 1, page_size: int = 20, max_page_size: int = 100):
    if page < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Page number must be >= 1")
    if page_size < 1 or page_size > max_page_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Page size must be between 1 and {max_page_size}",
        )
    return page, page_size


def validate_id_parameter(entity_id: int, entity_name: str = "Entity"):
    if entity_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{entity_name} ID must be positive",
        )
    return entity_id

