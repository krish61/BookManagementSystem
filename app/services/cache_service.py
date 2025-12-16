"""Cache service for Redis-based caching."""

import json
from typing import Optional, Any
import redis.asyncio as redis
from app.core.config import settings


class CacheService:
    """Service for handling Redis cache operations."""

    def __init__(self) -> None:
        """Initialize the cache service with Redis client."""
        self.redis_client: Optional[redis.Redis] = None
        self.ttl = settings.CACHE_TTL

    async def connect(self) -> None:
        """Establish connection to Redis."""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=(
                    settings.REDIS_PASSWORD
                    if settings.REDIS_PASSWORD
                    else None
                ),
                decode_responses=True,
            )
            # Test connection
            await self.redis_client.ping()
        except Exception:
            self.redis_client = None

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or Redis unavailable
        """
        if not self.redis_client:
            return None

        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {str(e)}")
            return None

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> bool:
        """
        Set a value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional, uses default if not provided)

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            ttl_seconds = ttl if ttl is not None else self.ttl
            serialized_value = json.dumps(value)
            await self.redis_client.setex(
                key, ttl_seconds, serialized_value
            )
            return True
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete a value from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {str(e)}")
            return False

    async def clear_pattern(self, pattern: str) -> bool:
        """
        Clear all keys matching a pattern.

        Args:
            pattern: Key pattern (e.g., "recommendations:*")

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            cursor = 0
            while True:
                cursor, keys = await self.redis_client.scan(
                    cursor, match=pattern, count=100
                )
                if keys:
                    await self.redis_client.delete(*keys)
                if cursor == 0:
                    break
            return True
        except Exception as e:
            print(f"Cache clear pattern error: {str(e)}")
            return False


# Global cache service instance
cache_service = CacheService()
