"""
Cache Manager - Redis caching for stock prices and news
Falls back gracefully if Redis unavailable
"""

import os
import json
import logging
from typing import Optional, Any
from datetime import timedelta

logger = logging.getLogger(__name__)

# Try to import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("⚠️  Redis not installed. Caching disabled. Install with: pip install redis")


class CacheManager:
    """
    Simple cache manager with Redis backend
    Gracefully falls back to no-cache if Redis unavailable
    """

    def __init__(self):
        self.redis_client = None
        self.enabled = False

        if not REDIS_AVAILABLE:
            logger.info("Cache: Disabled (redis not installed)")
            return

        # Try to connect to Redis
        redis_url = os.getenv("REDIS_URL")

        if redis_url:
            try:
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_timeout=2,
                    socket_connect_timeout=2
                )
                # Test connection
                self.redis_client.ping()
                self.enabled = True
                logger.info("✅ Cache enabled (Redis connected)")
            except Exception as e:
                logger.warning(f"⚠️  Redis connection failed: {e}. Caching disabled.")
                self.redis_client = None
                self.enabled = False
        else:
            logger.info("Cache: Disabled (REDIS_URL not set)")

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        Returns None if not found or cache unavailable
        """
        if not self.enabled or not self.redis_client:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                # Deserialize JSON
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        """
        Set value in cache with TTL (time to live)

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl_seconds: Time to live in seconds (default: 5 minutes)

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            # Serialize to JSON
            serialized = json.dumps(value)
            self.redis_client.setex(key, ttl_seconds, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern
        Example: clear_pattern("stock:*") deletes all stock price caches

        Returns:
            Number of keys deleted
        """
        if not self.enabled or not self.redis_client:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for '{pattern}': {e}")
            return 0

    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.enabled or not self.redis_client:
            return {"enabled": False, "status": "disabled"}

        try:
            info = self.redis_client.info("stats")
            return {
                "enabled": True,
                "status": "connected",
                "total_keys": self.redis_client.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"enabled": True, "status": "error", "error": str(e)}


# Global cache instance
cache = CacheManager()


# Convenience functions
def get_cached_stock_price(symbol: str) -> Optional[dict]:
    """Get cached stock price data"""
    return cache.get(f"stock:price:{symbol.upper()}")


def cache_stock_price(symbol: str, data: dict, ttl_seconds: int = 300):
    """
    Cache stock price data
    Default TTL: 5 minutes (300 seconds)
    """
    cache.set(f"stock:price:{symbol.upper()}", data, ttl_seconds)


def get_cached_news(symbol: str) -> Optional[list]:
    """Get cached news for symbol"""
    return cache.get(f"news:{symbol.upper()}")


def cache_news(symbol: str, news_list: list, ttl_seconds: int = 900):
    """
    Cache news data
    Default TTL: 15 minutes (900 seconds)
    """
    cache.set(f"news:{symbol.upper()}", news_list, ttl_seconds)


def clear_stock_caches():
    """Clear all stock price caches"""
    return cache.clear_pattern("stock:*")


def clear_news_caches():
    """Clear all news caches"""
    return cache.clear_pattern("news:*")


if __name__ == "__main__":
    # Test cache
    print("Testing Cache Manager...")
    print(f"Cache enabled: {cache.enabled}")

    if cache.enabled:
        # Test set/get
        cache.set("test:key", {"value": "hello"}, 60)
        result = cache.get("test:key")
        print(f"Test set/get: {result}")

        # Test stats
        stats = cache.get_stats()
        print(f"Cache stats: {stats}")

        # Cleanup
        cache.delete("test:key")
        print("✅ Cache test complete")
    else:
        print("⚠️  Cache not available for testing")
