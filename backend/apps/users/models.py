"""Custom User model with UUIDv7, JSONB preferences, and phone number."""
from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from uuid7 import uuid7


class User(AbstractUser):
    """
    Custom User model with:
    - UUIDv7 primary key for better indexing
    - JSONB preferences for flexible user settings
    - Phone number field with international support
    - Bio and avatar fields
    
    Note: We don't inherit from BaseModel here because AbstractUser
    already has its own id field. We manually add UUIDv7.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid7,
        editable=False,
    )
    email = models.EmailField(
        unique=True,
        db_index=True,
        help_text="User's email address (unique)",
    )
    phone_number = PhoneNumberField(
        blank=True,
        null=True,
        unique=True,
        help_text="User's phone number in international format (e.g., +1234567890)",
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        default="",
        help_text="User biography",
    )
    avatar = models.URLField(
        blank=True,
        default="",
        help_text="URL to user's avatar image",
    )
    preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="User preferences (theme, notifications, etc.)",
    )
    # Example preferences structure:
    # {
    #     "theme": "dark",
    #     "notifications": {
    #         "email": true,
    #         "push": false,
    #         "mentions": true
    #     },
    #     "privacy": {
    #         "show_email": false,
    #         "show_phone": false,
    #         "allow_messages": true
    #     }
    # }
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["username"], name="users_username_idx"),
            models.Index(fields=["email"], name="users_email_idx"),
            models.Index(fields=["created_at"], name="users_created_idx"),
        ]

    def __str__(self) -> str:
        return self.username

    @property
    def followers_count(self) -> int:
        """Get count of users following this user."""
        return self.followers.count()

    @property
    def following_count(self) -> int:
        """Get count of users this user is following."""
        return self.following.count()

    @property
    def posts_count(self) -> int:
        """Get count of posts by this user."""
        return self.posts.count()
