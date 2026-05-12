"""Redis connection manager for caching and pub/sub functionality."""

import json
from typing import Any, Optional, Union
import redis.asyncio as redis
from redis.asyncio import ConnectionPool
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from app.shared.core.settings import settings
from app.shared.core.logging import get_logger

logger = get_logger(__name__)


class RedisManager:
    """Async Redis connection manager with connection pooling."""
    
    _instance: Optional["RedisManager"] = None
    _pool: Optional[ConnectionPool] = None
    _client: Optional[redis.Redis] = None
    
    def __new__(cls) -> "RedisManager":
        """Singleton pattern for Redis manager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize(self) -> None:
        """Initialize Redis connection pool."""
        if self._client is not None:
            return
            
        try:
            # Ensure redis_url has decode_responses=True
            redis_url = settings.redis_url
            parsed = urlparse(redis_url)
            query_params = parse_qs(parsed.query or '')
            
            if "decode_responses" not in query_params:
                query_params["decode_responses"] = ["True"]
                new_query = urlencode(query_params, doseq=True)
                redis_url = urlunparse(parsed._replace(query=new_query))
            
            # Create connection pool with health check
            self._pool = ConnectionPool.from_url(
                redis_url,
                max_connections=settings.redis_max_connections,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30,  # Check connection health every 30 seconds
            )
            
            # Create Redis client
            self._client = redis.Redis(connection_pool=self._pool)
            
            # Test connection
            await self._client.ping()
            logger.info("Redis connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def close(self) -> None:
        """Close Redis connections."""
        if self._client:
            await self._client.close()
        if self._pool:
            await self._pool.disconnect()
        self._client = None
        self._pool = None
        logger.info("Redis connections closed")
    
    @property
    def client(self) -> redis.Redis:
        """Get Redis client (raises if not initialized)."""
        if self._client is None:
            raise RuntimeError("Redis manager not initialized. Call initialize() first.")
        return self._client
    
    async def get(self, key: str) -> Optional[Union[str, bytes]]:
        """Get value from Redis."""
        try:
            return await self._client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error for key '{key}': {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Union[str, bytes, dict, list], 
        ex: Optional[int] = None
    ) -> bool:
        """Set value in Redis with optional expiration."""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, default=str)
            elif not isinstance(value, (str, bytes)):
                value = str(value)
                
            return await self._client.set(key, value, ex=ex)
        except Exception as e:
            logger.error(f"Redis SET error for key '{key}': {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        try:
            return bool(await self._client.delete(key))
        except Exception as e:
            logger.error(f"Redis DELETE error for key '{key}': {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            return bool(await self._client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error for key '{key}': {e}")
            return False
    
    async def publish(self, channel: str, message: Union[str, dict, list]) -> int:
        """Publish message to Redis channel."""
        try:
            if isinstance(message, (dict, list)):
                message = json.dumps(message, default=str)
            elif not isinstance(message, str):
                message = str(message)
                
            return await self._client.publish(channel, message)
        except Exception as e:
            logger.error(f"Redis PUBLISH error for channel '{channel}': {e}")
            return 0
    
    async def subscribe(self, *channels: str):
        """Subscribe to Redis channels."""
        try:
            pubsub = self._client.pubsub()
            await pubsub.subscribe(*channels)
            return pubsub
        except Exception as e:
            logger.error(f"Redis SUBSCRIBE error for channels {channels}: {e}")
            raise
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter in Redis."""
        try:
            return await self._client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis INCREMENT error for key '{key}': {e}")
            return None
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key."""
        try:
            return bool(await self._client.expire(key, seconds))
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key '{key}': {e}")
            return False


# Global Redis manager instance
redis_manager = RedisManager()
