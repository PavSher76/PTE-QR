"""
Cache service for Redis operations
"""

import json
import os
from typing import Any, Dict, List, Optional

import redis.asyncio as redis
import structlog
from app.core.config import settings

logger = structlog.get_logger()

# Check if we're in test mode
TESTING = os.getenv("TESTING", "false").lower() == "true"


class MockCacheService:
    """Mock cache service for tests"""

    def __init__(self):
        self._cache = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        return self._cache.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        self._cache[key] = value
        return True

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return key in self._cache

    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        result = {}
        for key in keys:
            if key in self._cache:
                result[key] = self._cache[key]
        return result

    async def set_many(
        self, mapping: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Set multiple values in cache"""
        self._cache.update(mapping)
        return True

    async def delete_many(self, keys: List[str]) -> int:
        """Delete multiple keys from cache"""
        count = 0
        for key in keys:
            if key in self._cache:
                del self._cache[key]
                count += 1
        return count

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        # Simple pattern matching for tests
        keys_to_delete = [key for key in self._cache.keys() if pattern in key]
        for key in keys_to_delete:
            del self._cache[key]
        return len(keys_to_delete)

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter in cache"""
        current = self._cache.get(key, 0)
        new_value = current + amount
        self._cache[key] = new_value
        return new_value

    async def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """Decrement counter in cache"""
        current = self._cache.get(key, 0)
        new_value = current - amount
        self._cache[key] = new_value
        return new_value

    async def health_check(self) -> Dict[str, Any]:
        """Check cache health"""
        return {"status": "healthy", "type": "mock", "keys_count": len(self._cache)}

    async def close(self):
        """Close mock cache"""
        pass


class CacheService:
    """Redis cache service"""

    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.default_ttl = settings.CACHE_TTL_SECONDS
        self._redis = None

    async def _get_redis(self) -> redis.Redis:
        """Get Redis connection"""
        if self._redis is None:
            self._redis = redis.from_url(
                self.redis_url, encoding="utf-8", decode_responses=True
            )
        return self._redis

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            redis_client = await self._get_redis()
            value = await redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error("Cache get failed", key=key, error=str(e))
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            redis_client = await self._get_redis()
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)
            await redis_client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.error("Cache set failed", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            redis_client = await self._get_redis()
            result = await redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error("Cache delete failed", key=key, error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            redis_client = await self._get_redis()
            result = await redis_client.exists(key)
            return result > 0
        except Exception as e:
            logger.error("Cache exists check failed", key=key, error=str(e))
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration for key"""
        try:
            redis_client = await self._get_redis()
            result = await redis_client.expire(key, ttl)
            return result
        except Exception as e:
            logger.error("Cache expire failed", key=key, error=str(e))
            return False

    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        try:
            redis_client = await self._get_redis()
            values = await redis_client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value:
                    result[key] = json.loads(value)
            return result
        except Exception as e:
            logger.error("Cache get_many failed", keys=keys, error=str(e))
            return {}

    async def set_many(
        self, mapping: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Set multiple values in cache"""
        try:
            redis_client = await self._get_redis()
            ttl = ttl or self.default_ttl

            # Serialize values
            serialized_mapping = {
                key: json.dumps(value, default=str) for key, value in mapping.items()
            }

            # Set values
            await redis_client.mset(serialized_mapping)

            # Set expiration for all keys
            if ttl > 0:
                pipe = redis_client.pipeline()
                for key in mapping.keys():
                    pipe.expire(key, ttl)
                await pipe.execute()

            return True
        except Exception as e:
            logger.error("Cache set_many failed", error=str(e))
            return False

    async def delete_many(self, keys: List[str]) -> int:
        """Delete multiple keys from cache"""
        try:
            redis_client = await self._get_redis()
            result = await redis_client.delete(*keys)
            return result
        except Exception as e:
            logger.error("Cache delete_many failed", keys=keys, error=str(e))
            return 0

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            redis_client = await self._get_redis()
            keys = await redis_client.keys(pattern)
            if keys:
                result = await redis_client.delete(*keys)
                return result
            return 0
        except Exception as e:
            logger.error("Cache clear_pattern failed", pattern=pattern, error=str(e))
            return 0

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter in cache"""
        try:
            redis_client = await self._get_redis()
            result = await redis_client.incrby(key, amount)
            return result
        except Exception as e:
            logger.error("Cache increment failed", key=key, error=str(e))
            return None

    async def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """Decrement counter in cache"""
        try:
            redis_client = await self._get_redis()
            result = await redis_client.decrby(key, amount)
            return result
        except Exception as e:
            logger.error("Cache decrement failed", key=key, error=str(e))
            return None

    async def health_check(self) -> Dict[str, Any]:
        """Check cache health"""
        try:
            redis_client = await self._get_redis()
            info = await redis_client.info()

            return {
                "status": "healthy",
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            logger.error("Cache health check failed", error=str(e))
            return {"status": "unhealthy", "error": str(e)}

    async def close(self):
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
            self._redis = None


# Global cache service instance
cache_service = MockCacheService() if TESTING else CacheService()
