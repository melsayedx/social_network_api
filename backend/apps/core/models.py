"""Base models with UUIDv7 primary keys."""
from django.db import models
from uuid7 import uuid7


class BaseModel(models.Model):
    """
    Abstract base model with UUIDv7 primary key and timestamps.
    
    UUIDv7 is time-ordered, providing better B-tree index locality
    and insert performance compared to UUIDv4.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid7,
        editable=False,
        help_text="UUIDv7 - time-ordered for better indexing",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Record creation timestamp",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Record last update timestamp",
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.id}>"
