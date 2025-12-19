"""
Caching utilities and decorators for performance optimization.

Uses Redis as the caching backend with sensible TTLs.
"""
from functools import wraps
from typing import Callable

from django.core.cache import cache


# Cache TTLs (in seconds)
CACHE_TTL_SHORT = 60  # 1 minute
CACHE_TTL_MEDIUM = 300  # 5 minutes
CACHE_TTL_LONG = 3600  # 1 hour
CACHE_TTL_DAY = 86400  # 24 hours


def cache_key(*args) -> str:
    """Generate a cache key from arguments."""
    return ":".join(str(arg) for arg in args)


def cached(prefix: str, ttl: int = CACHE_TTL_MEDIUM):
    """
    Decorator to cache function results.
    
    Usage:
        @cached("user_profile", ttl=300)
        def get_user_profile(user_id):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key = cache_key(prefix, func.__name__, *args, *kwargs.values())
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result, ttl)
            return result
        
        return wrapper
    return decorator


def invalidate_cache(prefix: str, *args) -> None:
    """Invalidate a specific cache key."""
    key = cache_key(prefix, *args)
    cache.delete(key)


def invalidate_cache_pattern(pattern: str) -> None:
    """
    Invalidate all cache keys matching a pattern.
    
    Note: This requires Redis and uses SCAN for pattern matching.
    """
    try:
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")
        
        # Use SCAN to find matching keys (non-blocking)
        cursor = 0
        while True:
            cursor, keys = redis_conn.scan(cursor, match=f"*{pattern}*", count=100)
            if keys:
                redis_conn.delete(*keys)
            if cursor == 0:
                break
    except ImportError:
        # Fallback: clear entire cache (not ideal but works)
        cache.clear()


class CacheManager:
    """Manager for common caching operations."""
    
    # Cache key prefixes
    PREFIX_USER = "user"
    PREFIX_POST = "post"
    PREFIX_FEED = "feed"
    PREFIX_FOLLOWERS = "followers"
    PREFIX_FOLLOWING = "following"
    
    @classmethod
    def get_user_cache_key(cls, user_id: str) -> str:
        """Get cache key for user profile."""
        return cache_key(cls.PREFIX_USER, user_id)
    
    @classmethod
    def get_post_cache_key(cls, post_id: str) -> str:
        """Get cache key for post."""
        return cache_key(cls.PREFIX_POST, post_id)
    
    @classmethod
    def get_feed_cache_key(cls, user_id: str, page: int = 1) -> str:
        """Get cache key for user's feed."""
        return cache_key(cls.PREFIX_FEED, user_id, f"page_{page}")
    
    @classmethod
    def get_followers_cache_key(cls, user_id: str) -> str:
        """Get cache key for followers count."""
        return cache_key(cls.PREFIX_FOLLOWERS, user_id)
    
    @classmethod
    def cache_user(cls, user_id: str, data: dict, ttl: int = CACHE_TTL_MEDIUM) -> None:
        """Cache user profile data."""
        cache.set(cls.get_user_cache_key(user_id), data, ttl)
    
    @classmethod
    def get_cached_user(cls, user_id: str) -> dict | None:
        """Get cached user profile data."""
        return cache.get(cls.get_user_cache_key(user_id))
    
    @classmethod
    def invalidate_user(cls, user_id: str) -> None:
        """Invalidate user cache."""
        cache.delete(cls.get_user_cache_key(user_id))
    
    @classmethod
    def cache_feed(cls, user_id: str, data: list, page: int = 1, ttl: int = CACHE_TTL_SHORT) -> None:
        """Cache user's feed (short TTL for freshness)."""
        cache.set(cls.get_feed_cache_key(user_id, page), data, ttl)
    
    @classmethod
    def get_cached_feed(cls, user_id: str, page: int = 1) -> list | None:
        """Get cached feed."""
        return cache.get(cls.get_feed_cache_key(user_id, page))
    
    @classmethod
    def invalidate_feed(cls, user_id: str) -> None:
        """Invalidate all feed pages for a user."""
        invalidate_cache_pattern(f"{cls.PREFIX_FEED}:{user_id}")
