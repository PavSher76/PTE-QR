"""
Redis cache management
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

import redis.asyncio as redis
import structlog
from app.core.config import settings

logger = structlog.get_logger()


class CacheManager:
    """Redis cache manager"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._connection_lock = asyncio.Lock()

    async def _get_redis_client(self) -> redis.Redis:
        """Get Redis client with connection pooling"""
        if self.redis_client is None:
            async with self._connection_lock:
                if self.redis_client is None:
                    try:
                        self.redis_client = redis.from_url(
                            settings.REDIS_URL,
                            encoding="utf-8",
                            decode_responses=True,
                            socket_connect_timeout=5,
                            socket_timeout=5,
                            retry_on_timeout=True,
                            health_check_interval=30,
                        )

                        # Test connection
                        await self.redis_client.ping()
                        logger.info("Redis connection established")

                    except Exception as e:
                        logger.error("Failed to connect to Redis", error=str(e))
                        raise

        return self.redis_client

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            client = await self._get_redis_client()
            value = await client.get(key)

            if value is None:
                return None

            # Try to deserialize JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Return as string if not JSON
                return value

        except Exception as e:
            logger.error("Failed to get from cache", key=key, error=str(e))
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            client = await self._get_redis_client()

            # Serialize value
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, default=str)
            else:
                serialized_value = str(value)

            # Set with TTL
            if ttl:
                await client.setex(key, ttl, serialized_value)
            else:
                await client.set(key, serialized_value)

            return True

        except Exception as e:
            logger.error("Failed to set cache", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        try:
            client = await self._get_redis_client()
            result = await client.delete(key)
            return result > 0

        except Exception as e:
            logger.error("Failed to delete from cache", key=key, error=str(e))
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete keys matching pattern

        Args:
            pattern: Key pattern (supports * wildcard)

        Returns:
            Number of keys deleted
        """
        try:
            client = await self._get_redis_client()

            # Find keys matching pattern
            keys = await client.keys(pattern)

            if not keys:
                return 0

            # Delete keys in batches
            deleted_count = 0
            batch_size = 1000

            for i in range(0, len(keys), batch_size):
                batch = keys[i : i + batch_size]
                result = await client.delete(*batch)
                deleted_count += result

            logger.info("Deleted cache keys", pattern=pattern, count=deleted_count)
            return deleted_count

        except Exception as e:
            logger.error(
                "Failed to delete pattern from cache", pattern=pattern, error=str(e)
            )
            return 0

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        try:
            client = await self._get_redis_client()
            result = await client.exists(key)
            return result > 0

        except Exception as e:
            logger.error("Failed to check cache existence", key=key, error=str(e))
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration time for key

        Args:
            key: Cache key
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            client = await self._get_redis_client()
            result = await client.expire(key, ttl)
            return result

        except Exception as e:
            logger.error(
                "Failed to set cache expiration", key=key, ttl=ttl, error=str(e)
            )
            return False

    async def get_ttl(self, key: str) -> int:
        """
        Get time to live for key

        Args:
            key: Cache key

        Returns:
            TTL in seconds (-1 if no expiration, -2 if key doesn't exist)
        """
        try:
            client = await self._get_redis_client()
            return await client.ttl(key)

        except Exception as e:
            logger.error("Failed to get cache TTL", key=key, error=str(e))
            return -2

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment numeric value in cache

        Args:
            key: Cache key
            amount: Amount to increment by

        Returns:
            New value or None if failed
        """
        try:
            client = await self._get_redis_client()
            return await client.incrby(key, amount)

        except Exception as e:
            logger.error(
                "Failed to increment cache value", key=key, amount=amount, error=str(e)
            )
            return None

    async def get_keys(self, pattern: str = "*") -> List[str]:
        """
        Get keys matching pattern

        Args:
            pattern: Key pattern (supports * wildcard)

        Returns:
            List of matching keys
        """
        try:
            client = await self._get_redis_client()
            return await client.keys(pattern)

        except Exception as e:
            logger.error("Failed to get cache keys", pattern=pattern, error=str(e))
            return []

    async def clear_all(self) -> bool:
        """
        Clear all cache data

        Returns:
            True if successful, False otherwise
        """
        try:
            client = await self._get_redis_client()
            await client.flushdb()
            logger.info("All cache data cleared")
            return True

        except Exception as e:
            logger.error("Failed to clear cache", error=str(e))
            return False

    async def health_check(self) -> Dict[str, Any]:
        """
        Check cache health

        Returns:
            Health check results
        """
        try:
            client = await self._get_redis_client()

            # Test basic operations
            test_key = "health_check_test"
            test_value = "test"

            # Set and get test
            await client.setex(test_key, 10, test_value)
            retrieved_value = await client.get(test_key)
            await client.delete(test_key)

            # Get Redis info
            info = await client.info()

            return {
                "redis": "healthy",
                "connected": True,
                "test_passed": retrieved_value == test_value,
                "memory_used": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "uptime": info.get("uptime_in_seconds", 0),
            }

        except Exception as e:
            logger.error("Cache health check failed", error=str(e))
            return {"redis": "unhealthy", "connected": False, "error": str(e)}

    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
            logger.info("Redis connection closed")


# Global cache manager instance
cache_manager = CacheManager()
