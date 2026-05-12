"""Cache decorators and utilities for Redis caching."""

import functools
import hashlib
import json
from typing import Any, Callable, Optional, Union
import asyncio
import inspect

from app.shared.core.redis import redis_manager
from app.shared.core.logging import get_logger

logger = get_logger(__name__)


def cache_key_builder(
    prefix: str,
    func_name: str,
    args: tuple,
    kwargs: dict,
    include_args: bool = True,
    include_kwargs: bool = True
) -> str:
    """Build cache key from function name and arguments."""
    key_parts = [prefix, func_name]
    
    if include_args and args:
        # Skip first argument if it's 'self' (instance method)
        # Check if first argument looks like an instance (has __class__ but not a basic type)
        if args and len(args) > 0:
            first_arg = args[0]
            # Check if first argument is likely 'self' (instance method)
            # Basic types like int, str, bool, etc. are not 'self'
            basic_types = (int, str, bool, float, type(None))
            if hasattr(first_arg, '__class__') and not isinstance(first_arg, basic_types):
                # This looks like an instance method, skip 'self'
                args_to_hash = args[1:]
            else:
                # This looks like a regular function call, include all args
                args_to_hash = args
        else:
            args_to_hash = args
            
        if args_to_hash:
            args_str = json.dumps(args_to_hash, default=str, sort_keys=True)
            args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
            key_parts.append(f"args:{args_hash}")
    
    if include_kwargs and kwargs:
        kwargs_str = json.dumps(kwargs, default=str, sort_keys=True)
        kwargs_hash = hashlib.md5(kwargs_str.encode()).hexdigest()[:8]
        key_parts.append(f"kwargs:{kwargs_hash}")
    
    return ":".join(key_parts)


def cached(
    prefix: str = "cache",
    ttl: Optional[int] = None,
    include_args: bool = True,
    include_kwargs: bool = True,
    key_builder: Optional[Callable] = None
):
    """Decorator to cache async function results in Redis."""
    
    def decorator(func: Callable) -> Callable:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("@cached decorator only supports async functions in FastAPI applications")
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(func.__name__, args, kwargs)
            else:
                cache_key = cache_key_builder(
                    prefix, func.__name__, args, kwargs, include_args, include_kwargs
                )
            
            # Try to get from cache
            cached_result = await redis_manager.get(cache_key)
            if cached_result is not None:
                try:
                    # Handle both string and bytes responses
                    if isinstance(cached_result, bytes):
                        cached_result = cached_result.decode('utf-8')
                    
                    # Try to parse as JSON if it looks like JSON
                    if isinstance(cached_result, str) and cached_result.startswith(('{', '[')):
                        parsed = json.loads(cached_result)
                        # Preserve original types for domain entities
                        return parsed
                    else:
                        # Return as-is for primitive types (int, str, etc.)
                        return cached_result
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return cached_result
            
            # Execute function and cache result
            try:
                result = await func(*args, **kwargs)
                
                # Cache the result
                success = await redis_manager.set(cache_key, result, ex=ttl)
                if success:
                    logger.debug(f"Cached result for key: {cache_key}")
                else:
                    logger.warning(f"Failed to cache result for key: {cache_key}")
                
                return result
                
            except Exception as e:
                logger.error(f"Error executing cached function {func.__name__}: {e}")
                raise
        
        return async_wrapper
    
    return decorator


def invalidate_cache_pattern(pattern: str) -> Callable:
    """Decorator to invalidate cache keys matching pattern after function execution."""
    
    def decorator(func: Callable) -> Callable:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("@invalidate_cache_pattern decorator only supports async functions in FastAPI applications")
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                # Execute the function
                result = await func(*args, **kwargs)
                
                # Invalidate cache keys matching pattern using SCAN (non-blocking)
                try:
                    deleted_count = 0
                    cursor = 0
                    scan_pattern = f"*{pattern}*"
                    
                    while True:
                        cursor, keys = await redis_manager.client.scan(
                            cursor, match=scan_pattern, count=100
                        )
                        if keys:
                            deleted_count += await redis_manager.client.delete(*keys)
                        
                        # Exit when cursor returns to 0
                        if cursor == 0:
                            break
                    
                    if deleted_count > 0:
                        logger.debug(f"Invalidated {deleted_count} cache keys matching pattern: {pattern}")
                        
                except Exception as e:
                    logger.error(f"Error invalidating cache pattern '{pattern}': {e}")
                
                return result
                
            except Exception as e:
                logger.error(f"Error executing cache invalidation function {func.__name__}: {e}")
                raise
        
        return async_wrapper
    
    return decorator


def invalidate_cache_key(key: str) -> Callable:
    """Decorator to invalidate specific cache key after function execution."""
    
    def decorator(func: Callable) -> Callable:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("@invalidate_cache_key decorator only supports async functions in FastAPI applications")
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                # Execute the function
                result = await func(*args, **kwargs)
                
                # Invalidate specific cache key
                success = await redis_manager.delete(key)
                if success:
                    logger.debug(f"Invalidated cache key: {key}")
                else:
                    logger.debug(f"Cache key not found for invalidation: {key}")
                
                return result
                
            except Exception as e:
                logger.error(f"Error executing cache invalidation function {func.__name__}: {e}")
                raise
        
        return async_wrapper
    
    return decorator


class CacheHelper:
    """Helper class for manual cache operations."""
    
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Get value from cache."""
        return await redis_manager.get(key)
    
    @staticmethod
    async def set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        return await redis_manager.set(key, value, ex=ttl)
    
    @staticmethod
    async def delete(key: str) -> bool:
        """Delete key from cache."""
        return await redis_manager.delete(key)
    
    @staticmethod
    async def exists(key: str) -> bool:
        """Check if key exists in cache."""
        return await redis_manager.exists(key)
    
    @staticmethod
    async def invalidate_pattern(pattern: str) -> int:
        """Delete all keys matching pattern using SCAN (non-blocking)."""
        try:
            deleted_count = 0
            cursor = 0
            scan_pattern = f"*{pattern}*"
            
            while True:
                cursor, keys = await redis_manager.client.scan(
                    cursor, match=scan_pattern, count=100
                )
                if keys:
                    deleted_count += await redis_manager.client.delete(*keys)
                
                # Exit when cursor returns to 0
                if cursor == 0:
                    break
            
            return deleted_count
        except Exception as e:
            logger.error(f"Error invalidating cache pattern '{pattern}': {e}")
            return 0
