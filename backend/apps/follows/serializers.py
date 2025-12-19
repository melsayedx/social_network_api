"""Follow serializers."""
from rest_framework import serializers

from apps.users.serializers import UserSerializer

from .models import Follow


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for follow relationships."""
    
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ["id", "follower", "following", "created_at"]


class FollowerSerializer(serializers.ModelSerializer):
    """Serializer for listing followers."""
    
    user = UserSerializer(source="follower", read_only=True)
    
    class Meta:
        model = Follow
        fields = ["user", "created_at"]


class FollowingSerializer(serializers.ModelSerializer):
    """Serializer for listing following."""
    
    user = UserSerializer(source="following", read_only=True)
    
    class Meta:
        model = Follow
        fields = ["user", "created_at"]
