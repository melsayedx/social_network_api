"""Comment views with idempotent creation."""
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.response import Response

from apps.core.idempotency import idempotent
from apps.core.pagination import SmallPagination
from apps.core.permissions import IsOwnerOrReadOnly
from apps.posts.models import Post

from .models import Comment
from .serializers import CommentCreateSerializer, CommentSerializer


class CommentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for Comment operations.
    
    list: GET /api/v1/posts/{post_id}/comments/
    create: POST /api/v1/posts/{post_id}/comments/ (idempotent)
    destroy: DELETE /api/v1/comments/{id}/
    """
    
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = SmallPagination
    
    def get_serializer_class(self):
        if self.action == "create":
            return CommentCreateSerializer
        return CommentSerializer
    
    def get_queryset(self):
        """Filter by post_id if provided in URL."""
        queryset = super().get_queryset().select_related("user")
        
        post_id = self.kwargs.get("post_id")
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        post_id = self.kwargs.get("post_id")
        if post_id and self.request.method == "POST":
            context["post"] = get_object_or_404(Post, pk=post_id)
        return context
    
    @idempotent
    def create(self, request, *args, **kwargs):
        """Create a new comment (idempotent with X-Idempotency-Key header)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )

