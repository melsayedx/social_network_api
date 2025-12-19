"""Comment model."""
from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class Comment(BaseModel):
    """
    Comment model for post comments.
    
    Uses UUIDv7 primary key inherited from BaseModel.
    """
    
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="The post this comment belongs to",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="Comment author",
    )
    content = models.TextField(
        max_length=500,
        help_text="Comment content",
    )

    class Meta:
        db_table = "comments"
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["post", "-created_at"], name="comments_post_idx"),
            models.Index(fields=["user", "-created_at"], name="comments_user_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user.username} on {self.post_id}: {self.content[:30]}..."
    
    def save(self, *args, **kwargs):
        """Override save to update post comment count."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Increment comment count on post
            from apps.posts.models import Post
            Post.objects.filter(pk=self.post_id).update(
                comments_count=models.F("comments_count") + 1
            )
    
    def delete(self, *args, **kwargs):
        """Override delete to update post comment count."""
        post_id = self.post_id
        super().delete(*args, **kwargs)
        
        # Decrement comment count on post
        from apps.posts.models import Post
        Post.objects.filter(pk=post_id).update(
            comments_count=models.F("comments_count") - 1
        )
