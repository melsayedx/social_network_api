"""
ViewSet mixins for common functionality and optimization.
"""
from rest_framework import mixins


class OptimizedQueryMixin:
    """
    Mixin that provides optimized querysets with select_related/prefetch_related.
    
    Set `select_related_fields` and `prefetch_related_fields` on the viewset.
    
    Usage:
        class PostViewSet(OptimizedQueryMixin, GenericViewSet):
            select_related_fields = ["user"]
            prefetch_related_fields = ["comments__user"]
    """
    
    select_related_fields: list[str] = []
    prefetch_related_fields: list[str] = []
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)
        
        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)
        
        return queryset


class CachedListMixin:
    """
    Mixin that caches list responses.
    
    Set `cache_prefix` and optionally `cache_ttl` on the viewset.
    Uses user-specific cache keys for authenticated users.
    """
    
    cache_prefix: str = ""
    cache_ttl: int = 60  # 1 minute default
    
    def list(self, request, *args, **kwargs):
        from apps.core.cache import cache_key, CACHE_TTL_SHORT
        from django.core.cache import cache
        
        if not self.cache_prefix:
            return super().list(request, *args, **kwargs)
        
        # Build cache key with query params
        user_id = str(request.user.id) if request.user.is_authenticated else "anon"
        query_string = request.GET.urlencode()
        key = cache_key(self.cache_prefix, user_id, query_string)
        
        # Try cache
        cached_response = cache.get(key)
        if cached_response is not None:
            return self.get_paginated_response(cached_response) if self.paginator else cached_response
        
        # Get fresh data
        response = super().list(request, *args, **kwargs)
        
        # Cache the data (not the Response object)
        cache.set(key, response.data, self.cache_ttl)
        
        return response


class BulkCreateMixin:
    """
    Mixin for bulk creation of objects.
    
    POST with a list of objects to create multiple at once.
    """
    
    def get_serializer(self, *args, **kwargs):
        # Allow list input for bulk creation
        if isinstance(kwargs.get("data"), list):
            kwargs["many"] = True
        return super().get_serializer(*args, **kwargs)


class ActionPermissionMixin:
    """
    Mixin that allows per-action permission classes.
    
    Set `action_permissions` dict on the viewset.
    
    Usage:
        class PostViewSet(ActionPermissionMixin, GenericViewSet):
            action_permissions = {
                "create": [IsAuthenticated],
                "like": [IsAuthenticated],
                "list": [AllowAny],
            }
    """
    
    action_permissions: dict = {}
    
    def get_permissions(self):
        if self.action in self.action_permissions:
            return [perm() for perm in self.action_permissions[self.action]]
        return super().get_permissions()
