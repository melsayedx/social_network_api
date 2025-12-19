"""Comment serializers."""
from rest_framework import serializers

from apps.users.serializers import UserSerializer

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments."""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ["id", "user", "content", "created_at"]
        read_only_fields = ["id", "user", "created_at"]


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments."""
    
    class Meta:
        model = Comment
        fields = ["content"]
    
    def validate_content(self, value: str) -> str:
        """Validate content is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Comment content cannot be empty.")
        return value.strip()
    
    def create(self, validated_data: dict) -> Comment:
        """Create comment with user and post from context."""
        comment = Comment.objects.create(
            user=self.context["request"].user,
            post=self.context["post"],
            content=validated_data["content"],
        )
        return comment
