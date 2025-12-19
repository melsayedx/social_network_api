"""Follow views using GenericViewSet with mixins."""
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.models import User

from .models import Follow
from .serializers import FollowerSerializer, FollowingSerializer
from .services import FollowService


class FollowViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for Follow operations.
    
    toggle: POST /api/v1/users/{username}/follow/
    followers: GET /api/v1/users/{username}/followers/
    following: GET /api/v1/users/{username}/following/
    """
    
    queryset = Follow.objects.all()
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        if self.action == "followers":
            return FollowerSerializer
        return FollowingSerializer
    
    def get_queryset(self):
        """Filter by username from URL."""
        queryset = super().get_queryset()
        username = self.kwargs.get("username")
        
        if username:
            if self.action == "followers":
                queryset = queryset.filter(following__username=username).select_related("follower")
            elif self.action == "following":
                queryset = queryset.filter(follower__username=username).select_related("following")
        
        return queryset
    
    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="toggle",
    )
    def toggle(self, request, username=None):
        """
        Toggle follow status for a user.
        
        POST /api/v1/users/{username}/follow/
        """
        user_to_follow = get_object_or_404(User, username=username)
        
        try:
            is_following, followers_count = FollowService.toggle_follow(
                request.user,
                user_to_follow,
            )
            return Response({
                "following": is_following,
                "followers_count": followers_count,
            })
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    @action(detail=False, methods=["get"])
    def followers(self, request, username=None):
        """
        List followers of a user.
        
        GET /api/v1/users/{username}/followers/
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def following(self, request, username=None):
        """
        List users that a user is following.
        
        GET /api/v1/users/{username}/following/
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
