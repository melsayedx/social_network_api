"""Post model with JSONB metadata."""
from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.db import models

from apps.core.models import BaseModel


class Post(BaseModel):
    """
    Post model with:
    - UUIDv7 primary key (inherited from BaseModel)
    - JSONB metadata for hashtags, mentions, media
    - Denormalized likes_count for performance
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
        help_text="Post author",
    )
    content = models.TextField(
        max_length=500,
        help_text="Post content (max 500 characters)",
    )
    likes_count = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Denormalized like count for performance",
    )
    comments_count = models.PositiveIntegerField(
        default=0,
        help_text="Denormalized comment count for performance",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Flexible metadata (hashtags, mentions, media)",
    )
    # Example metadata structure:
    # {
    #     "hashtags": ["python", "django", "api"],
    #     "mentions": ["uuid-of-user-1", "uuid-of-user-2"],
    #     "media": [
    #         {"type": "image", "url": "https://..."},
    #         {"type": "link", "url": "https://...", "title": "..."}
    #     ],
    #     "edited": true,
    #     "edit_history": [{"content": "old content", "edited_at": "2024-..."}]
    # }

    class Meta:
        db_table = "posts"
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at", "user"], name="posts_timeline_idx"),
            models.Index(fields=["user", "-created_at"], name="posts_user_timeline_idx"),
            models.Index(fields=["-likes_count"], name="posts_popular_idx"),
            GinIndex(fields=["metadata"], name="posts_metadata_gin"),
        ]

    def __str__(self) -> str:
        return f"{self.user.username}: {self.content[:50]}..."

    @property
    def is_edited(self) -> bool:
        """Check if post has been edited."""
        return self.metadata.get("edited", False)
    
    @property
    def hashtags(self) -> list[str]:
        """Get list of hashtags from metadata."""
        return self.metadata.get("hashtags", [])
