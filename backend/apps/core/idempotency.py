"""
Idempotency support for POST operations.

Prevents duplicate operations when clients retry requests by using
an idempotency key header. Results are cached and returned on retry.

Usage:
    Client sends: X-Idempotency-Key: <unique-key>
    
    First request: Executes normally, caches result
    Retry with same key: Returns cached result (no duplicate operation)
"""
import hashlib
import json
from functools import wraps
from typing import Callable

from django.core.cache import cache
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response


# Cache TTL for idempotency keys (24 hours)
IDEMPOTENCY_TTL = 86400

# Header name for idempotency key
IDEMPOTENCY_HEADER = "HTTP_X_IDEMPOTENCY_KEY"
IDEMPOTENCY_HEADER_NAME = "X-Idempotency-Key"


class IdempotencyError(Exception):
    """Raised when there's an issue with idempotency processing."""
    pass


def get_idempotency_key(request: Request) -> str | None:
    """Extract idempotency key from request headers."""
    return request.META.get(IDEMPOTENCY_HEADER)


def generate_request_fingerprint(request: Request) -> str:
    """
    Generate a fingerprint of the request to detect conflicting keys.
    
    If the same idempotency key is used with different request bodies,
    we should reject the request.
    """
    data = {
        "method": request.method,
        "path": request.path,
        "body": str(request.data),
        "user": str(request.user.id) if request.user.is_authenticated else "anon",
    }
    content = json.dumps(data, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()


def get_cache_key(idempotency_key: str) -> str:
    """Generate cache key for storing idempotent response."""
    return f"idempotency:{idempotency_key}"


def get_fingerprint_key(idempotency_key: str) -> str:
    """Generate cache key for storing request fingerprint."""
    return f"idempotency:fp:{idempotency_key}"


def store_idempotent_response(
    idempotency_key: str,
    fingerprint: str,
    response_data: dict,
    status_code: int,
) -> None:
    """Store response for idempotent retrieval."""
    cache_key = get_cache_key(idempotency_key)
    fingerprint_key = get_fingerprint_key(idempotency_key)
    
    cache.set(cache_key, {
        "data": response_data,
        "status": status_code,
    }, IDEMPOTENCY_TTL)
    
    cache.set(fingerprint_key, fingerprint, IDEMPOTENCY_TTL)


def get_idempotent_response(idempotency_key: str) -> dict | None:
    """Retrieve stored idempotent response."""
    cache_key = get_cache_key(idempotency_key)
    return cache.get(cache_key)


def get_stored_fingerprint(idempotency_key: str) -> str | None:
    """Retrieve stored request fingerprint."""
    fingerprint_key = get_fingerprint_key(idempotency_key)
    return cache.get(fingerprint_key)


def idempotent(func: Callable) -> Callable:
    """
    Decorator to make a view action idempotent.
    
    Usage:
        class PostViewSet(GenericViewSet):
            @idempotent
            def create(self, request, *args, **kwargs):
                ...
    
    The client must send X-Idempotency-Key header with a unique key.
    If the same key is reused, the original response is returned.
    """
    @wraps(func)
    def wrapper(self, request: Request, *args, **kwargs) -> Response:
        idempotency_key = get_idempotency_key(request)
        
        # If no idempotency key, process normally
        if not idempotency_key:
            return func(self, request, *args, **kwargs)
        
        # Check for existing response
        stored_response = get_idempotent_response(idempotency_key)
        
        if stored_response:
            # Verify fingerprint matches (same key, different request = error)
            stored_fingerprint = get_stored_fingerprint(idempotency_key)
            current_fingerprint = generate_request_fingerprint(request)
            
            if stored_fingerprint and stored_fingerprint != current_fingerprint:
                return Response(
                    {
                        "error": {
                            "code": "IDEMPOTENCY_CONFLICT",
                            "message": "Idempotency key already used with different request.",
                        }
                    },
                    status=status.HTTP_409_CONFLICT,
                )
            
            # Return cached response
            response = Response(
                stored_response["data"],
                status=stored_response["status"],
            )
            response["X-Idempotent-Replayed"] = "true"
            return response
        
        # Execute the actual function
        response = func(self, request, *args, **kwargs)
        
        # Only cache successful responses (2xx)
        if 200 <= response.status_code < 300:
            fingerprint = generate_request_fingerprint(request)
            store_idempotent_response(
                idempotency_key,
                fingerprint,
                response.data,
                response.status_code,
            )
        
        return response
    
    return wrapper


class IdempotencyMiddleware:
    """
    Middleware to handle idempotency for all POST/PUT/PATCH requests.
    
    Add to MIDDLEWARE in settings.py if you want automatic idempotency
    for all mutating requests.
    """
    
    IDEMPOTENT_METHODS = {"POST", "PUT", "PATCH"}
    
    def __init__(self, get_response: Callable):
        self.get_response = get_response
    
    def __call__(self, request):
        # Only check idempotency for mutating methods
        if request.method not in self.IDEMPOTENT_METHODS:
            return self.get_response(request)
        
        idempotency_key = request.META.get(IDEMPOTENCY_HEADER)
        
        # If no key provided, process normally
        if not idempotency_key:
            return self.get_response(request)
        
        # Check for cached response
        stored = get_idempotent_response(idempotency_key)
        
        if stored:
            from django.http import JsonResponse
            response = JsonResponse(stored["data"], status=stored["status"])
            response["X-Idempotent-Replayed"] = "true"
            return response
        
        # Process request normally
        response = self.get_response(request)
        
        # Cache successful responses
        if 200 <= response.status_code < 300:
            try:
                import json
                data = json.loads(response.content)
                store_idempotent_response(
                    idempotency_key,
                    "",  # No fingerprint check in middleware mode
                    data,
                    response.status_code,
                )
            except (json.JSONDecodeError, AttributeError):
                pass  # Skip caching non-JSON responses
        
        return response
