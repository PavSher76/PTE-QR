"""
Test cache service with mocked Redis
"""

import asyncio
from typing import Any, Optional

import structlog

from app.core.test_config import test_settings

logger = structlog.get_logger()


class MockRedis:
    """Mock Redis client for tests"""

    def __init__(self):
        self._cache = {}

    async def get(self, key: str) -> Optional[bytes]:
        """Get value from cache"""
        logger.debug("Mock Redis get", key=key)
        return self._cache.get(key)

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set value in cache"""
        logger.debug("Mock Redis set", key=key, ex=ex)
        self._cache[key] = value
        return True

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        logger.debug("Mock Redis delete", key=key)
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        logger.debug("Mock Redis exists", key=key)
        return key in self._cache

    async def flushall(self) -> bool:
        """Clear all cache"""
        logger.debug("Mock Redis flushall")
        self._cache.clear()
        return True

    async def ping(self) -> bool:
        """Ping Redis"""
        logger.debug("Mock Redis ping")
        return True

    async def close(self):
        """Close connection"""
        logger.debug("Mock Redis close")
        pass


class TestCacheService:
    """Test cache service with mocked Redis"""

    def __init__(self):
        self.redis = MockRedis()
        self.enabled = test_settings.CACHE_ENABLED
        self.ttl = test_settings.CACHE_TTL_SECONDS

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None

        try:
            value = await self.redis.get(key)
            if value:
                logger.debug("Cache hit", key=key)
                return value
            else:
                logger.debug("Cache miss", key=key)
                return None
        except Exception as e:
            logger.error("Cache get failed", key=key, error=str(e))
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        if not self.enabled:
            return True

        try:
            ttl = ttl or self.ttl
            await self.redis.set(key, value, ex=ttl)
            logger.debug("Cache set", key=key, ttl=ttl)
            return True
        except Exception as e:
            logger.error("Cache set failed", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.enabled:
            return True

        try:
            await self.redis.delete(key)
            logger.debug("Cache delete", key=key)
            return True
        except Exception as e:
            logger.error("Cache delete failed", key=key, error=str(e))
            return False

    async def health_check(self) -> dict:
        """Check cache health"""
        try:
            await self.redis.ping()
            return {"status": "healthy", "type": "mock", "enabled": self.enabled}
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "type": "mock",
                "enabled": self.enabled,
            }

    async def clear(self):
        """Clear all cache"""
        try:
            await self.redis.flushall()
            logger.debug("Cache cleared")
        except Exception as e:
            logger.error("Cache clear failed", error=str(e))


# Create test cache service instance
test_cache_service = TestCacheService()
