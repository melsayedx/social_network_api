"""Follow model."""
from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class Follow(BaseModel):
    """
    Follow model for user following relationships.
    
    Uses UUIDv7 primary key inherited from BaseModel.
    follower follows following.
    """
    
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
        help_text="The user who is following",
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers",
        help_text="The user being followed",
    )

    class Meta:
        db_table = "follows"
        verbose_name = "Follow"
        verbose_name_plural = "Follows"
        # Prevent duplicate follows and self-follows
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"],
                name="unique_follow",
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F("following")),
                name="no_self_follow",
            ),
        ]
        indexes = [
            models.Index(fields=["follower", "following"], name="follows_pair_idx"),
            models.Index(fields=["following", "-created_at"], name="follows_followers_idx"),
            models.Index(fields=["follower", "-created_at"], name="follows_following_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.follower.username} follows {self.following.username}"
