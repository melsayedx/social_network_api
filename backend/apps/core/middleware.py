"""
Database middleware for query monitoring and optimization.

Logs slow queries and provides query counting for debugging.
"""
import logging
import time
from functools import wraps
from typing import Callable

from django.conf import settings
from django.db import connection, reset_queries

logger = logging.getLogger(__name__)


class QueryCountMiddleware:
    """
    Middleware to count and log database queries per request.
    
    Only active in DEBUG mode.
    """
    
    def __init__(self, get_response: Callable):
        self.get_response = get_response
    
    def __call__(self, request):
        if not settings.DEBUG:
            return self.get_response(request)
        
        reset_queries()
        start_time = time.time()
        
        response = self.get_response(request)
        
        total_time = time.time() - start_time
        query_count = len(connection.queries)
        
        # Add headers for debugging
        response["X-Query-Count"] = str(query_count)
        response["X-Query-Time"] = f"{total_time:.3f}s"
        
        # Log if too many queries (potential N+1)
        if query_count > 10:
            logger.warning(
                f"High query count: {query_count} queries for {request.path} "
                f"in {total_time:.3f}s"
            )
        
        return response


class SlowQueryMiddleware:
    """
    Middleware to log slow queries.
    
    Queries exceeding the threshold are logged with full SQL for analysis.
    """
    
    SLOW_QUERY_THRESHOLD_MS = 100  # Log queries > 100ms
    
    def __init__(self, get_response: Callable):
        self.get_response = get_response
    
    def __call__(self, request):
        if not settings.DEBUG:
            return self.get_response(request)
        
        reset_queries()
        response = self.get_response(request)
        
        for query in connection.queries:
            query_time_ms = float(query.get("time", 0)) * 1000
            if query_time_ms > self.SLOW_QUERY_THRESHOLD_MS:
                logger.warning(
                    f"Slow query ({query_time_ms:.0f}ms): {query['sql'][:200]}"
                )
        
        return response


def log_queries(func: Callable) -> Callable:
    """
    Decorator to log queries made during a function call.
    
    Useful for debugging specific views or services.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        reset_queries()
        result = func(*args, **kwargs)
        
        query_count = len(connection.queries)
        if query_count > 0:
            logger.debug(
                f"{func.__name__}: {query_count} queries"
            )
            for i, query in enumerate(connection.queries, 1):
                logger.debug(f"  [{i}] {query['sql'][:100]}...")
        
        return result
    
    return wrapper


def get_query_count() -> int:
    """Get the current query count (useful in tests)."""
    return len(connection.queries)


def reset_query_count() -> None:
    """Reset the query counter."""
    reset_queries()
