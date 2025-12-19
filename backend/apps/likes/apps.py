"""Likes app configuration."""
from django.apps import AppConfig


class LikesConfig(AppConfig):
    """Likes app config."""
    
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.likes"
    verbose_name = "Likes"
