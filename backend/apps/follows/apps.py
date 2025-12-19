"""Follows app configuration."""
from django.apps import AppConfig


class FollowsConfig(AppConfig):
    """Follows app config."""
    
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.follows"
    verbose_name = "Follows"
