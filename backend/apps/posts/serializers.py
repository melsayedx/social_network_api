"""Post serializers."""
from rest_framework import serializers

from apps.users.serializers import UserSerializer

from .models import Post


class PostListSerializer(serializers.ModelSerializer):
    """Serializer for post list view (minimal data for performance)."""
    
    user = UserSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            "id",
            "user",
            "content",
            "likes_count",
            "comments_count",
            "is_liked",
            "created_at",
        ]
        read_only_fields = ["id", "likes_count", "comments_count", "created_at"]
    
    def get_is_liked(self, obj: Post) -> bool:
        """Check if the current user has liked this post."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            # This will be populated by a prefetch in the viewset
            if hasattr(obj, "_user_liked"):
                return obj._user_liked
            return obj.likes.filter(user=request.user).exists()
        return False


class PostDetailSerializer(PostListSerializer):
    """Serializer for post detail view (includes metadata)."""
    
    metadata = serializers.JSONField(read_only=True)
    is_edited = serializers.BooleanField(read_only=True)
    hashtags = serializers.ListField(read_only=True)
    
    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ["metadata", "is_edited", "hashtags", "updated_at"]


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating posts."""
    
    hashtags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        write_only=True,
    )
    
    class Meta:
        model = Post
        fields = ["content", "hashtags"]
    
    def validate_content(self, value: str) -> str:
        """Validate content is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Post content cannot be empty.")
        return value.strip()
    
    def create(self, validated_data: dict) -> Post:
        """Create post with metadata."""
        hashtags = validated_data.pop("hashtags", [])
        user = self.context["request"].user
        
        metadata = {}
        if hashtags:
            metadata["hashtags"] = [h.lower().strip("#") for h in hashtags]
        
        post = Post.objects.create(
            user=user,
            content=validated_data["content"],
            metadata=metadata,
        )
        return post


class PostUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating posts."""
    
    class Meta:
        model = Post
        fields = ["content"]
    
    def update(self, instance: Post, validated_data: dict) -> Post:
        """Update post and track edit history."""
        if "content" in validated_data and validated_data["content"] != instance.content:
            # Track edit in metadata
            metadata = instance.metadata or {}
            metadata["edited"] = True
            
            edit_history = metadata.get("edit_history", [])
            edit_history.append({
                "content": instance.content,
                "edited_at": instance.updated_at.isoformat(),
            })
            metadata["edit_history"] = edit_history[-5:]  # Keep last 5 edits
            
            instance.metadata = metadata
        
        return super().update(instance, validated_data)
