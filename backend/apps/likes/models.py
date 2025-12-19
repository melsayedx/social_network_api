"""Like model."""
from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class Like(BaseModel):
    """
    Like model for post likes.
    
    Uses UUIDv7 primary key inherited from BaseModel.
    Unique constraint on (user, post) to prevent duplicate likes.
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes",
        help_text="User who liked the post",
    )
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="likes",
        help_text="The liked post",
    )

    class Meta:
        db_table = "likes"
        verbose_name = "Like"
        verbose_name_plural = "Likes"
        # Unique constraint to prevent duplicate likes
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                name="unique_user_post_like",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "post"], name="likes_user_post_idx"),
            models.Index(fields=["post", "-created_at"], name="likes_post_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user.username} liked post {self.post_id}"
