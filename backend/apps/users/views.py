"""User views using GenericViewSet for maintainability."""
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import User
from .serializers import (
    UserDetailSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class AuthViewSet(viewsets.GenericViewSet):
    """
    ViewSet for authentication-related actions.
    
    register: POST /api/v1/auth/register/
    """
    
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=["post"], serializer_class=UserRegistrationSerializer)
    def register(self, request):
        """
        Register a new user.
        
        Password is hashed using Argon2 (configured in settings).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "User registered successfully.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for user operations.
    
    list: GET /api/v1/users/
    retrieve: GET /api/v1/users/{username}/
    me: GET/PATCH /api/v1/users/me/
    posts: GET /api/v1/users/{username}/posts/
    """
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "username"
    search_fields = ["username", "bio"]
    ordering_fields = ["username", "created_at"]
    ordering = ["-created_at"]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "me" and self.request.method in ["PATCH", "PUT"]:
            return UserUpdateSerializer
        if self.action == "me":
            return UserDetailSerializer
        if self.action == "posts":
            from apps.posts.serializers import PostListSerializer
            return PostListSerializer
        return UserSerializer
    
    @action(
        detail=False,
        methods=["get", "patch"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request):
        """
        Retrieve or update the currently authenticated user.
        
        GET: Returns full profile with email, phone, preferences
        PATCH: Update bio, avatar, phone_number, preferences
        """
        if request.method == "GET":
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        
        # PATCH
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserDetailSerializer(request.user).data)
    
    @action(detail=True, methods=["get"])
    def posts(self, request, username=None):
        """
        List posts by a specific user.
        
        GET /api/v1/users/{username}/posts/
        """
        from apps.posts.models import Post
        
        user = self.get_object()
        posts = Post.objects.filter(user=user).select_related("user")
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
