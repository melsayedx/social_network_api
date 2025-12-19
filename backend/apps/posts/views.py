"""Post views with performance optimizations and idempotency."""
from django.db.models import Exists, OuterRef
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.cache import CacheManager, CACHE_TTL_SHORT
from apps.core.idempotency import idempotent
from apps.core.mixins import OptimizedQueryMixin
from apps.core.permissions import IsOwnerOrReadOnly
from apps.likes.models import Like

from .models import Post
from .serializers import (
    PostCreateSerializer,
    PostDetailSerializer,
    PostListSerializer,
    PostUpdateSerializer,
)
from .services import PostService


class PostViewSet(
    OptimizedQueryMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for Post operations with performance optimizations.
    
    Features:
    - Idempotent create (use X-Idempotency-Key header)
    - select_related for user (eliminates N+1)
    - Annotated is_liked for current user
    - Cached following feed
    
    list: GET /api/v1/posts/
    create: POST /api/v1/posts/ (idempotent with header)
    retrieve: GET /api/v1/posts/{id}/
    partial_update: PATCH /api/v1/posts/{id}/
    destroy: DELETE /api/v1/posts/{id}/
    like: POST /api/v1/posts/{id}/like/
    following: GET /api/v1/posts/following/
    """
    
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    select_related_fields = ["user"]  # From OptimizedQueryMixin
    filterset_fields = ["user__username"]
    search_fields = ["content"]
    ordering_fields = ["created_at", "likes_count"]
    ordering = ["-created_at"]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return PostCreateSerializer
        if self.action in ["update", "partial_update"]:
            return PostUpdateSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        return PostListSerializer
    
    @idempotent
    def create(self, request, *args, **kwargs):
        """
        Create a new post (idempotent).
        
        Send X-Idempotency-Key header to prevent duplicate posts on retry.
        """
        return super().create(request, *args, **kwargs)
    
    def get_queryset(self):
        """Optimize queryset with is_liked annotation for authenticated users."""
        queryset = super().get_queryset()
        
        # Annotate with is_liked for authenticated users
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                _user_liked=Exists(
                    Like.objects.filter(
                        post=OuterRef("pk"),
                        user=self.request.user,
                    )
                )
            )
        
        return queryset
    
    def perform_update(self, serializer):
        """Use service layer for update to track edit history."""
        instance = self.get_object()
        content = serializer.validated_data.get("content", instance.content)
        PostService.update_post(instance, content)
    
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """Toggle like on a post (invalidates cache)."""
        post = self.get_object()
        liked, likes_count = PostService.toggle_like(request.user, post)
        
        # Invalidate feed caches when like status changes
        CacheManager.invalidate_feed(str(request.user.id))
        
        return Response({"liked": liked, "likes_count": likes_count})
    
    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def following(self, request):
        """
        Get posts from followed users (cached for performance).
        
        GET /api/v1/posts/following/
        """
        user_id = str(request.user.id)
        page = request.query_params.get("page", 1)
        
        # Try cache first
        cached_data = CacheManager.get_cached_feed(user_id, page)
        if cached_data is not None:
            return self.get_paginated_response(cached_data)
        
        # Get fresh data
        following_ids = request.user.following.values_list("following_id", flat=True)
        queryset = self.get_queryset().filter(user_id__in=following_ids)
        
        page_obj = self.paginate_queryset(queryset)
        if page_obj is not None:
            serializer = self.get_serializer(page_obj, many=True)
            
            # Cache the serialized data
            CacheManager.cache_feed(user_id, serializer.data, page, CACHE_TTL_SHORT)
            
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
