"""Comments app configuration."""
from django.apps import AppConfig


class CommentsConfig(AppConfig):
    """Comments app config."""
    
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.comments"
    verbose_name = "Comments"
